# SURL

![GitHub Release](https://img.shields.io/github/v/release/neojelll/url-shortener?include_prereleases&display_name=release&style=flat-square)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/neojelll/url-shortener/.github%2Fworkflows%2Fpublish.yml?style=flat-square)
![Static Badge](https://img.shields.io/badge/coverage-unknow-white?style=flat-square)
![Static Badge](https://img.shields.io/badge/python-3.12-blue?style=flat-square)
![GitHub Repo stars](https://img.shields.io/github/stars/neojelll/url-shortener)

A link shortener is a handy tool, long long hair, complex URLs in short places, easy to remember links. Ideal for routing traffic on your social media pages, email campaigns and websites. Simplify your links and track their performance in one place!

## Use Cases

### General

* A user submits a request with a link that he wants to shorten using cURL

  Parameter|Default value|Description
  -|-|-
  expiration | 1 day | link validity time
  prefix | empty string | link prefix

* In response he receives a short link
* When using a short link, it will be redirected to the original one
* If the link has expired, the user will receive a static page in response with information that the link did not exist or is no longer valid

### WebUI

All the same as described in General, using SPA (Single Page Application) WebUI

### Telegram

All the same as described in General, using a bot in Telegram

## Architecture

### Containers Diagram

![Container](architecture/diagrams/container-diagram.png)
