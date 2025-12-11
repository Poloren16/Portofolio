#include <iostream>
#include "gameproject.h"

adr_game createGame(string kode, string namaGame, string genre, string platform, string deadline, string server){
    adr_game G = new elmGame;
    infoG(G).kode = kode;
    infoG(G).namaGame = namaGame;
    infoG(G).genre = genre;
    infoG(G).platform = platform;
    infoG(G).deadline = deadline;
    infoG(G).server = server;
    nextGame(G) = NULL;
    return G;
}
void inserLastGame(listGame &Lg, adr_game G) {
    if (firstGame(G) == NULL) {
        firstGame(G) = G;
        lastGame(G) = G;
    } else {
        nextGame(lastGame(Lg) = G;
        lastGame(Lg) = G;
    }
}

void addRelation(adr_game G, adr_develop D) {
    if (firstR(G) == NULL) {
        firstR(G) = D;
    } else {
        nextDev(D) = firstR(G);
        firstR(G) = D;
    }
    cout << "Relasi dibuat di game: " << infoG(G).namaGame << endl;
    cout << "Karyawan: " << infoD(D).nama << endl;
}

void deleteFirstGame(listGame &Lg){
    adr_game G;
    adr_develop D;
    adr_develop tempD;
    if (firstGame(Lg) == NULL) {
        cout << "List game kosong" << endl;
    }

    G = firstGame(Lg);
    while (firstR != NULL) {
        Q = firstR(G);
        firstR(G) = nextDev(D);
    }

    if (firstGame(Lg) == lastGame(Lg)) {
        firstGame(Lg) = NULL;
        lastGame(Lg) = NULL;
    } else {
        firstGame(Lg) = nextGame(firstGame(Lg));
        lastGame(firstGame(Lg)) = NULL;
    }

    delete P;
    cout << "Game Berhasil Dihapus" << endl;
}

adr_develop createKaryawan(string nama, string ID, string peran){
    adr_develop D = new elmDev;
    infoD(D).nama = nama;
    infoD(D).ID = ID;
    infoD(D).peran = peran;
    nextDev(D) = NULL;
    return D;
}

void insertFirstKaryawan(listDev &Ld, adr_develop D){
    if (firsDevelop(Ld) == NULL) {
        firsDevelop(Ld) = D;
    } else {
        nextDev(D) = firsDevelop(Ld);
        firsDevelop(Ld) = D;
    }
}

void deleteLastKaryawan(listDev &Ld, listGame &Lg){
    void deleteLastKaryawanAndRelation(List &LChild, ListGame &Lg) {
    if (firstDevelop(Ld) == NULL) {
        cout << "List Karyawan kosong" << endl;

    }
    if (nextDev(firstDevelop(Ld)) == NULL) {

        adr_game G = firstGame(Lg);
        while (G != NULL) {
            if (firstR(G) == firstDevelop(Ld)) {
                firstR(G) = NULL;
            } else {
                adr_develop D = firstR(G);
                while (D != NULL) {
                    if (nextDev(D) == firstDevelop(Ld)) {
                        nextDev(D) = NULL;
                        break;
                    }
                    D = nextDev(D);
                }
            }
            G = nextGame(G);
        }


        delete firstDevelop(Ld);
        firstDevelop(Ld) = NULL;
        cout << "Elemen terakhir dari List Child beserta relasinya berhasil dihapus." << endl;
        return;
    }


    adr_develop P = firstDevelop(Ld);
    R = NULL;

    while (nextDev(P) != NULL) {
        D = P;
        P = nextDev(P);
    }

    while (G != NULL) {
        if (firstR(G) == P) {
            firstR(G) = NULL;
        } else {
            adr_develop temp = firstR(G);
            while (temp != NULL) {
                if (nextDev(temp) == P) {
                    nextDev(temp) = NULL;
                    break;
                }
                temp = nextDev(temp);
            }
        }
        G = nextGame(G);
    }


    if (Q != NULL) {
        nextDev(D) = NULL;
    } else {

        firstDevelop(Ld) = NULL;
    }


    delete P;
    cout << "List Karyawan dan Relasi dihapus" << endl;
    }
}

void deleteRelation(adr_game &G, adr_develop &D) {
    if (G == NULL || D == NULL) {
        cout << "Tidak ada relasi yang dihapus" << endl;
    }

    if(firstR(G) == D) {
        firstR(G) = nextDev(D);
    } else {
        adr_develop temp = firstR(G);
        while (temp != NULL && nextDev(temp) != D) {
            temp = nextDev(temp);
        }
        if (temp != NULL) {
            nextDev(temp) = nextDev(D);
        }
    }
    cout << "Game : " << infoG(G).namaGame << endl;
    cout << "Karyawan : " << infoG(G).nama << endl;
}

void showGame(listGame &Lg) {
    if (firstGame(Lg) == NULL) {
        cout << "List Game Kosong" << endl;
    }
    G = firstGame(Lg);
    while (G != NULL) {
        cout << "Kode : " << infoG(G).kode << endl;
        cout << "Nama Game : " << infoG(G).namaGame << endl;
        cout << "Genre : " << infoG(G).genre << endl;
        cout << "Platform : " << infoG(G).platform << endl;
        cout << "Deadline : " << infoG(G).deadline << endl;
        cout << "Server : " << infoG(G).server << endl;
        G = nextGame(G);
    }
}

void showKaryawan(listDev &Ld) {
    if (firstGame(Lg) == NULL) {
        cout << "List Karyawan Kosong" << endl;
    }
    D = firsDevelop(Ld);
    while (D != NULL) {
        cout << "Nama : " << infoD(D).nama << endl;
        cout << "ID : " << infoD(D).ID << endl;
        cout << "Peran : " << infoD(D).peran << endl;
        D = nextDev(D);
    }
}

