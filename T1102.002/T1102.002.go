package main

import (
	"bytes"
	"context"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
	"time"

	"golang.org/x/text/encoding/charmap"
	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

const (
	token       = "token" // Замените на токен вашего бота
	logFileName = "bot.log"                // Имя файла для логов
	commandTimeout = 30 * time.Second     // Тайм-аут для выполнения команд
)

func main() {
	// Настраиваем логирование
	logFile, err := os.OpenFile(logFileName, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Printf("Ошибка при создании файла логов: %v\n", err)
		return
	}
	defer logFile.Close()
	log.SetOutput(logFile)
	log.SetFlags(log.Ldate | log.Ltime | log.Lshortfile)

	// Создаем бота
	bot, err := tgbotapi.NewBotAPI(token)
	if err != nil {
		log.Fatalf("Ошибка при создании бота: %v\n", err)
		return
	}
	log.Printf("Бот авторизован под аккаунтом %s\n", bot.Self.UserName)

	// Настраиваем обновления
	u := tgbotapi.NewUpdate(0)
	u.Timeout = 60

	updates := bot.GetUpdatesChan(u)

	log.Println("Бот ожидает обновления...")

	// Обрабатываем обновления
	for update := range updates {
		if update.Message == nil || update.Message.Text == "" {
			log.Printf("Пропущено обновление: тип данных не текстовый. Детали: %+v\n", update)
			continue
		}

		// Логируем входящее сообщение
		log.Printf("Получено сообщение от пользователя %s: %s\n", update.Message.From.UserName, update.Message.Text)

		userMessage := update.Message.Text
		chatID := update.Message.Chat.ID

		if strings.HasPrefix(userMessage, "/cmd ") {
			// Выполняем команду
			command := strings.TrimPrefix(userMessage, "/cmd ")
			output, err := executeShellCommand(command)
			if err != nil {
				errorMessage := fmt.Sprintf("Ошибка выполнения команды '%s': %v", command, err)
				log.Println(errorMessage)
				bot.Send(tgbotapi.NewMessage(chatID, errorMessage))
				continue
			}
			if output == "" {
				output = "Команда выполнена успешно, но вывода нет."
			}
			bot.Send(tgbotapi.NewMessage(chatID, fmt.Sprintf("Вывод:\n%s", output)))
		} else if strings.HasPrefix(userMessage, "/upload ") {
			// Загружаем файл
			filename := strings.TrimPrefix(userMessage, "/upload ")
			if err := sendFile(bot, chatID, filename); err != nil {
				bot.Send(tgbotapi.NewMessage(chatID, fmt.Sprintf("Ошибка загрузки файла: %v", err)))
			}
		} else {
			// Помощь по командам
			bot.Send(tgbotapi.NewMessage(chatID, "Команды:\n/cmd <команда> - выполнить команду\n/upload <файл> - загрузить файл"))
		}
	}
}

func executeShellCommand(command string) (string, error) {
	// Определяем платформу
	cmd := exec.Command("bash", "-c", command) // Unix-подобная система
	if os.PathSeparator == '\\' {             // Windows
		cmd = exec.Command("cmd", "/C", command)
	}

	// Захват stdout и stderr
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	// Устанавливаем контекст с тайм-аутом
	ctx, cancel := context.WithTimeout(context.Background(), commandTimeout)
	defer cancel()

	// Привязываем контекст к команде
	cmd = exec.CommandContext(ctx, cmd.Path, cmd.Args[1:]...)
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	err := cmd.Run()
	if ctx.Err() == context.DeadlineExceeded {
		log.Printf("Тайм-аут команды: %s\n", command)
		return "", fmt.Errorf("команда превысила время выполнения (%s)", commandTimeout)
	}

	if err != nil {
		log.Printf("Ошибка выполнения команды: %s\nstderr: %s\n", err.Error(), stderr.String())
		return "", fmt.Errorf("ошибка: %s, stderr: %s", err.Error(), stderr.String())
	}

	// Обрабатываем вывод для Windows (CP866 -> UTF-8)
	output := stdout.Bytes()
	if os.PathSeparator == '\\' { // Windows
		decoder := charmap.CodePage866.NewDecoder()
		output, err = decoder.Bytes(output)
		if err != nil {
			log.Printf("Ошибка декодирования вывода: %v\n", err)
			return "", fmt.Errorf("ошибка декодирования: %v", err)
		}
	}

	return string(output), nil
}

func sendFile(bot *tgbotapi.BotAPI, chatID int64, filename string) error {
	file, err := os.Open(filename)
	if err != nil {
		return fmt.Errorf("не удалось открыть файл: %v", err)
	}
	defer file.Close()

	document := tgbotapi.NewDocument(chatID, tgbotapi.FileReader{
		Name:   filename,
		Reader: file,
	})

	_, err = bot.Send(document)
	return err
}
