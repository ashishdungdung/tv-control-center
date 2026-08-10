#!/usr/bin/with-contenv bashio

TARGET_IP=$(bashio::config 'target_ip')

bashio::log.info "Starting BRAVIA Control Center for target ${TARGET_IP}..."

exec bravia-control serve --port 8888 --target "${TARGET_IP}"
