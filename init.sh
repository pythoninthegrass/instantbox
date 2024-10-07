#!/usr/bin/env bash

# shellcheck disable=SC2162

cat << 'DESCRIPTION' >/dev/null
Install script for instantbox
Home Page: https://github.com/pythoninthegrass/instantbox

Usage:
	mkdir -p instantbox && cd $_
	bash <(curl -sSL https://raw.githubusercontent.com/pythoninthegrass/instantbox/master/init.sh)"
	docker compose up -d
DESCRIPTION

check_cmd() {
	command -v "$1" >/dev/null 2>&1
}

dependencies=(curl docker docker-compose)

check_dependencies() {
	for dependency in "${dependencies[@]}"; do
		if ! check_cmd "$dependency" && [ "$dependency" != "docker-compose" ]; then
			echo "$dependency is not installed, please try again after it's installed"
			exit 1
		elif [ "$dependency" == "docker-compose" ]; then
			if ! check_cmd "$dependency"; then
				if ! check_cmd "docker" || ! docker compose version >/dev/null 2>&1; then
					echo "docker-compose is not installed, please try again after it's installed"
					exit 1
				fi
			fi
		fi
	done
}

setup_compose_file() {
	curl -sSLO https://raw.githubusercontent.com/pythoninthegrass/instantbox/master/docker-compose.yml
	echo "Enter your IP (optional): "
	read IP
	echo "Choose a port (default: 8888): "
	read PORT
	[[ -z "$IP" ]] || sed -i -e "s/SERVERURL=$/SERVERURL=$IP/" docker-compose.yml
	[[ -z "$PORT" ]] || sed -i -e "s/8888:80/$PORT:80/" docker-compose.yml
}

main() {
	echo -e "Welcome to instantbox, please wait...\n"

	check_dependencies
	setup_compose_file

	echo "You're all set! "
	echo "Run 'docker compose up -d' then go to http://${IP:-localhost}:${PORT:-8888} on your browser."
}

main
