# URL Shortener

![GitHub Release](https://img.shields.io/github/v/release/neojelll/url-shortener?include_prereleases&display_name=release&style=flat-square)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/neojelll/url-shortener/.github%2Fworkflows%2Fpublish.yml?style=flat-square)
![Static Badge](https://img.shields.io/badge/python-3.12-blue?style=flat-square)
![GitHub contributors](https://img.shields.io/github/contributors-anon/neojelll/url-shortener?style=social)
![GitHub Repo stars](https://img.shields.io/github/stars/neojelll/url-shortener?style=social)

## Use Cases

### General

* Пользователь отправляет запрос с ссылкой которую хочет сократить c помощью cURL

  Параметр|Значение по умолчанию|Описание
  -|-|-
  expiration | 1 сутки | время действия ссылки
  prefix | пустая строка | префикс ссылки

* В ответ получает короткую ссылку
* При использовании короткой ссылки будет перенаправлен по оригинальной
* Если время ссылки истекло, пользователь получит в ответ статическую страницу с информацией о том что ссылка не существовала либо уже не валидна

### WebUI

Все то же что описано в General, с помощью SPA (Single Page Application) WebUI

### Telegram

Все то же что описано в General, с помощью бота в Telegram

## Architecture

### Containers Diagram

![Container](architecture/diagrams/container-diagram.png)
