import socket               # Mengimpor modul socket untuk membuat koneksi TCP
import os                   # Mengimpor modul os untuk memeriksa dan membaca file
import time                 # Mengimpor modul time untuk memberi delay dan mengukur waktu

HOST = '0.0.0.0'            # Server akan menerima koneksi dari semua IP
PORT = 5880                 # Port yang digunakan server

# Fungsi untuk menangani request dari client
def handle_request(conn, addr):
    print(f"[STATUS] Sedang melayani klien dari {addr}...")
    start_time = time.time()   # Mencatat waktu mulai pelayanan

    try:
        request = conn.recv(1024).decode()  # Menerima dan mendekode request dari client
        print("Request:")
        print(request)                      # Menampilkan request di terminal

        lines = request.split('\r\n')       # Memecah request menjadi baris-baris
        if not lines:
            return                          # Jika kosong, keluar

        request_line = lines[0]             # Baris pertama adalah request line
        parts = request_line.split()        # Memisahkan method dan path
        if len(parts) < 2:
            return                          # Jika format tidak valid, keluar

        method, path = parts[0], parts[1]   # Mendapatkan metode dan path
        filename = path.lstrip('/')         # Menghapus '/' di awal path

        if method != 'GET':                 # Hanya mendukung GET
            time.sleep(10)                  # Simulasi delay
            response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
            conn.sendall(response.encode()) # Kirim response 405
            return

        if os.path.isfile(filename):        # Jika file ada
            with open(filename, 'rb') as f:
                content = f.read()          # Baca konten file
            time.sleep(10)                  # Delay sebelum kirim
            header = "HTTP/1.1 200 OK\r\n"
            header += f"Content-Length: {len(content)}\r\n"
            header += "Content-Type: text/html\r\n\r\n"
            conn.sendall(header.encode() + content)  # Kirim header + konten
        else:
            time.sleep(10)                  # Delay sebelum response
            response = "HTTP/1.1 404 Not Found\r\n\r\nFile not found"
            conn.sendall(response.encode()) # Kirim response 404

    finally:
        conn.close()                        # Tutup koneksi
        end_time = time.time()              # Catat waktu selesai
        elapsed = end_time - start_time     # Hitung durasi
        print(f"[STATUS] Selesai melayani klien dari {addr}. Waktu pelayanan: {elapsed:.4f} detik\n")

# Fungsi menjalankan server secara single-threaded
def run_single_threaded():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))           # Bind socket ke host dan port
        server.listen(1)                    # Menunggu maksimal 1 koneksi
        print(f"[MODE: SINGLE THREAD] Server listening on port {PORT}...\n")

        while True:
            conn, addr = server.accept()    # Terima koneksi dari client
            print(f"Connected by {addr}")
            handle_request(conn, addr)      # Tangani permintaan secara langsung (blocking)

# Entry point program
if __name__ == '__main__':
    run_single_threaded()                   # Jalankan server
