import socket               # Mengimpor modul socket untuk membuat dan mengelola koneksi TCP/IP
import os                   # Mengimpor modul os untuk memeriksa dan membaca file di sistem
import threading            # Mengimpor modul threading untuk memungkinkan multiple client ditangani secara bersamaan
import time                 # Mengimpor modul time untuk mencatat waktu dan memberikan delay simulasi

HOST = '0.0.0.0'            # Server akan menerima koneksi dari semua IP (bind ke semua interface jaringan)
PORT = 5880                 # Port yang digunakan server untuk menerima koneksi

# Fungsi untuk menangani permintaan client secara individual
def handle_request(conn, addr):
    print(f"[STATUS] Sedang melayani klien dari {addr}...")  # Log saat mulai menangani klien
    start_time = time.time()   # Mencatat waktu mulai pelayanan

    try:
        request = conn.recv(1024).decode()  # Menerima hingga 1024 byte data dari client, kemudian decode dari byte ke string
        print("Request:")
        print(request)                      # Menampilkan isi request HTTP dari client

        lines = request.split('\r\n')       # Memisahkan request menjadi baris-baris
        if not lines:
            return                          # Jika request kosong, keluar dari fungsi

        request_line = lines[0]             # Baris pertama dari HTTP request, biasanya seperti: GET /index.html HTTP/1.1
        parts = request_line.split()        # Memisahkan baris menjadi bagian-bagian (method, path, versi)
        if len(parts) < 2:
            return                          # Jika tidak cukup bagian (method dan path), keluar

        method, path = parts[0], parts[1]   # Ekstraksi method (GET) dan path (misalnya /index.html)
        filename = path.lstrip('/')         # Menghapus tanda '/' di awal path untuk mendapatkan nama file

        if method != 'GET':                 # Jika bukan metode GET, tidak dilayani
            time.sleep(10)                  # Simulasi delay pelayanan
            response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"  # Respons HTTP 405
            conn.sendall(response.encode()) # Kirim respons ke client
            return

        if os.path.isfile(filename):        # Cek apakah file dengan nama tersebut ada
            with open(filename, 'rb') as f: # Buka file dalam mode biner
                content = f.read()          # Baca seluruh isi file
            time.sleep(10)                  # Simulasi delay pelayanan
            header = "HTTP/1.1 200 OK\r\n"  # Buat header HTTP 200 OK
            header += f"Content-Length: {len(content)}\r\n"      # Tambahkan panjang konten
            header += "Content-Type: text/html\r\n\r\n"          # Tambahkan jenis konten
            conn.sendall(header.encode() + content)              # Kirim header + isi file ke client
        else:
            time.sleep(10)                  # Simulasi delay pelayanan
            response = "HTTP/1.1 404 Not Found\r\n\r\nFile not found"  # Respons jika file tidak ditemukan
            conn.sendall(response.encode()) # Kirim respons 404 ke client

    finally:
        conn.close()                        # Tutup koneksi socket
        end_time = time.time()              # Catat waktu selesai pelayanan
        elapsed = end_time - start_time     # Hitung durasi pelayanan
        print(f"[STATUS] Selesai melayani klien dari {addr}. Waktu pelayanan: {elapsed:.4f} detik\n")

# Fungsi utama untuk menjalankan server dalam mode multi-threaded
def run_multi_threaded():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server: # Membuat socket TCP
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Mengizinkan reuse port (hindari error bind saat restart)
        server.bind((HOST, PORT))           # Bind socket ke host dan port yang ditentukan
        server.listen()                     # Mulai mendengarkan koneksi masuk
        print(f"[MODE: MULTI THREAD] Server listening on port {PORT}...\n")

        while True:
            conn, addr = server.accept()    # Menerima koneksi baru dari client
            thread = threading.Thread(target=handle_request, args=(conn, addr))  # Buat thread baru untuk menangani client
            thread.start()                  # Jalankan thread

# Entry point program (dijalankan saat file ini dieksekusi langsung)
if __name__ == '__main__':
    run_multi_threaded()                    # Jalankan fungsi server multi-threaded
