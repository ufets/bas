#!/bin/bash

# Configuration
LOG_FILE="secrets_scan_$(date +%Y-%m-%d_%H-%M-%S).log"
KEY_PATTERNS='API_KEY|SECRET_KEY|TOKEN|PASSWORD|ACCESS_KEY|AWS_KEY|AUTH_KEY|PRIVATE_KEY|ENCRYPTION_KEY|CREDENTIALS'
FILE_PATTERNS='.*(env|gitlab|github|config|secret|key|token|password|credentials|\.npmrc|\.env|settings|configuration).*'
SEARCH_DIRS="/etc /opt /home /var /root ."
GITLAB_PATHS="/etc/gitlab /opt/gitlab /var/opt/gitlab /srv/gitlab"
GITHUB_PATHS="/etc/actions-runner /opt/runner /var/lib/github"

# Enable extended regex
shopt -s extglob

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Custom grep function with error suppression
safe_grep() {
    grep -ER -n -i "$KEY_PATTERNS" "$1" 2>/dev/null || true
}

# 1. Check environment variables
log "Checking environment variables..."
printenv | grep -E -i --color=always "$KEY_PATTERNS" | 
awk '{print "[ENV] Found in environment: "$0}' | tee -a "$LOG_FILE"

# 2. Search in filesystem
log "Scanning filesystem..."
find $SEARCH_DIRS -type f -iregex "$FILE_PATTERNS" -exec grep --color=always -H -E -n -i "$KEY_PATTERNS" {} + 2>/dev/null |
awk '{print "[FS] Potential secret: "$0}' | tee -a "$LOG_FILE"

# 3. GitLab specific checks
log "Checking GitLab..."
for gl_path in $GITLAB_PATHS; do
    if [ -d "$gl_path" ]; then
        find "$gl_path" -type f \( -name "*password*" -o -name "*token*" \) -exec grep --color=always -H -i "$KEY_PATTERNS" {} + 2>/dev/null |
        awk -v path="$gl_path" '{print "[GITLAB]["path"] "$0}' | tee -a "$LOG_FILE"
    fi
done

# 4. GitHub specific checks
log "Checking GitHub..."
for gh_path in $GITHUB_PATHS; do
    if [ -d "$gh_path" ]; then
        find "$gh_path" -type f \( -name "*.env" -o -name "*credentials*" \) -exec grep --color=always -H -i "$KEY_PATTERNS" {} + 2>/dev/null |
        awk -v path="$gh_path" '{print "[GITHUB]["path"] "$0}' | tee -a "$LOG_FILE"
    fi
done

# 5. Docker containers check
if command -v docker &> /dev/null; then
    log "Scanning Docker containers..."
    docker ps --format '{{.Names}}' | while read -r container; do
        log "Checking container: $container"
        
        # Check container environment
        docker exec "$container" sh -c 'printenv' | grep -E -i --color=always "$KEY_PATTERNS" |
        awk -v cont="$container" '{print "[DOCKER]["cont"] ENV: "$0}' | tee -a "$LOG_FILE"
        
        # Check GitLab in container
        for gl_path in $GITLAB_PATHS; do
            docker exec "$container" sh -c "[ -d '$gl_path' ] && find '$gl_path' -type f -exec grep -H -i '$KEY_PATTERNS' {} +" 2>/dev/null |
            awk -v cont="$container" -v path="$gl_path" '{print "[DOCKER]["cont"]["path"] "$0}' | tee -a "$LOG_FILE"
        done
        
        # Generic files check in container
        docker exec "$container" sh -c "find /etc /opt /root -type f \( -name '*token*' -o -name '*password*' \) -exec grep -H -i '$KEY_PATTERNS' {} +" 2>/dev/null |
        awk -v cont="$container" '{print "[DOCKER]["cont"] "$0}' | tee -a "$LOG_FILE"
    done
else
    log "Docker not found, skipping container checks"
fi

# 6. Git history and configs
log "Checking Git repositories..."
find . -type d -name .git | while read git_dir; do
    repo_dir=$(dirname "$git_dir")
    log "Scanning repository: $repo_dir"
    
    # Config files
    find "$repo_dir" -type f \( -name ".gitconfig" -o -name ".credentials" \) -exec grep --color=always -H -i "$KEY_PATTERNS" {} + 2>/dev/null |
    awk '{print "[GIT] Config: "$0}' | tee -a "$LOG_FILE"
    
    # Commit history
    git -C "$repo_dir" log -p --all -S "$KEY_PATTERNS" |
    awk '{print "[GIT] History: "$0}' | tee -a "$LOG_FILE"
done

log "Scan completed. Results saved to: $LOG_FILE"