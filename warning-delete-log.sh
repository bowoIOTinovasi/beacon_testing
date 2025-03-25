read -r -p "Are you sure delete all LOG? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY]) 
        rm log/ble/*
        rm log/ble_result/*
        rm log/wifi/*
        rm log/wifi_result/*
        ;;
    *)
        ls -l
        ;;
esac