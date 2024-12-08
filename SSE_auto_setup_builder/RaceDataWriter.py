# サーバーに接続
s = connect_to_server(HOST, port)

with open(TELEMETRY_CSV, 'w', newline='', encoding='utf-8') as csvfile:
    writer = None  # CSV書き込み用のオブジェクト（後で初期化）
    buffer = ""

    try:
        while True:
            # データを受信
            data = s.recv(BUFFER_SIZE).decode('utf-8')
            buffer += data

            # 完全なJSONオブジェクトを処理
            while '\n' in buffer:
                message, buffer = buffer.split('\n', 1)
                json_data = json.loads(message)
                
                if json_data['type'] == 'static':
                    # 静的データの処理
                    process_static_data(json_data['data'])
                elif json_data['type'] == 'telemetry':
                    # テレメトリーデータの処理
                    if writer is None:
                        # 最初のテレメトリーデータを受信したときにCSVのヘッダーを初期化
                        fieldnames = list(flatten_dict(json_data).keys()) + ['timestamp']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()

                    process_telemetry_data(json_data, writer)
                    csvfile.flush()  # データをすぐにファイルに書き込む

    except KeyboardInterrupt:
        print("データ収集を停止します...")
    finally:
        s.close()