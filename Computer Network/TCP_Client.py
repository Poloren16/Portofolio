import socket               # Untuk membuat koneksi jaringan (menggunakan TCP socket)
import threading            # Untuk membuat thread agar beberapa client bisa berjalan bersamaan
import time                 # Untuk memberi jeda (delay) antar client saat mengirim request
import sys                  # Untuk membaca argumen dari command-line

JUMLAH_CLIENT = 1           # Jumlah client yang ingin dijalankan (bisa diubah sesuai kebutuhan)

def kirim_request(nomor, host, port, filename):
    # Memberi jeda 5 detik antara masing-masing client berdasarkan urutan nomor
    time.sleep(5 * (nomor - 1))

    # Membuat socket TCP client
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        # Menghubungkan socket client ke server berdasarkan host dan port
        client.connect((host, port))

        # Menyusun HTTP GET request standar sesuai format HTTP/1.1
        request = f"GET /{filename} HTTP/1.1\r\nHost: {host}\r\n\r\n"
        client.sendall(request.encode())  # Mengirim request ke server dalam format byte

        response = b""  # Buffer untuk menyimpan seluruh data respons dari server
        while True:
            data = client.recv(1024)  # Menerima data sebanyak 1024 byte per iterasi
            if not data:             # Jika tidak ada data lagi diterima, keluar dari loop
                break
            response += data         # Menambahkan data ke buffer respons

        # Menampilkan hasil respons dari server ke terminal
        print(f"\n--- Response dari koneksi #{nomor} ---")
        print(response.decode(errors='ignore'))  # Menampilkan data sebagai teks (mengabaikan karakter error)

if __name__ == '__main__':
    # Memastikan jumlah argumen yang dimasukkan dari command-line adalah 3 (host, port, filename)
    if len(sys.argv) != 4:
        print("Penggunaan: python TCP_Client.py <host> <port> <filename>")
        sys.exit(1)  # Keluar dari program jika argumen tidak sesuai

    # Mengambil argumen dari command-line
    host_input = sys.argv[1]         # Argumen ke-1: alamat host (contoh: "127.0.0.1")
    port_input = int(sys.argv[2])    # Argumen ke-2: port server (contoh: 5880)
    filename_input = sys.argv[3]     # Argumen ke-3: nama file yang ingin diminta (contoh: "header.html")

    threads = []  # List untuk menyimpan semua thread client

    # Membuat dan menjalankan thread sebanyak JUMLAH_CLIENT
    for i in range(JUMLAH_CLIENT):
        # Membuat thread untuk menjalankan fungsi kirim_request dengan argumen yang sesuai
        t = threading.Thread(target=kirim_request, args=(i+1, host_input, port_input, filename_input))
        threads.append(t)  # Menyimpan thread ke list
        t.start()          # Menjalankan thread (client mulai mengirim request)

    # Menunggu semua thread selesai (supaya program tidak keluar sebelum semua client selesai)
    for t in threads:
        t.join()
