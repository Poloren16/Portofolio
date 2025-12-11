#include <iostream>
#include "gameproject.h"

using namespace std;

int main()
{
    listGame Lg;
    listDev Ld;
    adr_game G;
    adr_develop D;
    adr_game game1;
    adr_game game2;
    adr_develop karyawan1;
    adr_develop karyawan2;

    firstGame(Lg) = NULL;
    lastGame(Lg) = NULL;
    firsDevelop(Ld) = NULL;

    game1 = createGame('COC-STR-06', 'Clash of Clans', 'Strategy', 'Mobile', '06-04-2025', 'GoogleCloud(US-West)');
    inserLastGame(Lg, game1);
    game2 = createGame('WD-ACT-07', 'Watch Dogs', 'Action', 'PC', '08-08-2025', 'Azure(US-North)');
    inserLastGame(Lg, game2);

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
    return 0;

    karyawan1 =createGame('Thiago Shelv', 'TS06', '3D Artist');
    insertFirstKaryawan(Ld, karyawan1);
    adr_develop(game1, karyawan1);
    karyawan2 =createGame('Xaviera Redit', 'XR07', 'Writer');
    insertFirstKaryawan(Ld, karyawan2);
    adr_develop(game2, karyawan2);

    D = firsDevelop(Ld);
    while (D != NULL) {
        cout << "Nama : " << infoD(D).nama << endl;
        cout << "ID : " << infoD(D).ID << endl;
        cout << "Peran : " << infoD(D).peran << endl;
        D = nextDev(D);
    }

    while (D != NULL) {
        cout << "Nama : " << infoD(D).nama << endl;
        cout << "ID : " << infoD(D).ID << endl;
        cout << "Peran : " << infoD(D).peran << endl;
        D = nextDev(D);
    }

    cout << "Relasi antara Game dan Karyawan: " << endl;
    while (G != NULL) {
        cout << "Game: " << infoG(G).namaGame << endl;
        D = firstR(G);
        while (D != NULL) {
            cout << "Nama : " << infoD(D).nama << endl;
            cout << "ID : " << infoD(D).ID << endl;
            cout << "Peran : " << infoD(D).peran << endl;
            D = nextDev(D);
        }
        G = nextGame(G);
    }

    deleteFirstGame(Lg, Ld);
    cout << "Data Game Setelah Dihapus" << endl;
    while (G != NULL) {
        cout << "Kode : " << infoG(G).kode << endl;
        cout << "Nama Game : " << infoG(G).namaGame << endl;
        cout << "Genre : " << infoG(G).genre << endl;
        cout << "Platform : " << infoG(G).platform << endl;
        cout << "Deadline : " << infoG(G).deadline << endl;
        cout << "Server : " << infoG(G).server << endl;
        G = nextGame(G);
    }


 cout << "Relasi antara Game dan Karyawan setelah dihapus : " << endl;
    while (G != NULL) {
        cout << "Game: " << infoG(G).namaGame << endl;
        D = firstR(G);
        while (D != NULL) {
            cout << "Nama : " << infoD(D).nama << endl;
            cout << "ID : " << infoD(D).ID << endl;
            cout << "Peran : " << infoD(D).peran << endl;
            D = nextDev(D);
        }
        G = nextGame(G);
    }


    deleteLastKaryawan(Ld, Lg);
    while (D != NULL) {
        cout << "Nama : " << infoD(D).nama << endl;
        cout << "ID : " << infoD(D).ID << endl;
        cout << "Peran : " << infoD(D).peran << endl;
        D = nextDev(D);
    }
    cout << "Relasi antara Game dan Karyawan setelah dihapus : " << endl;
    while (G != NULL) {
        cout << "Game: " << infoG(G).namaGame << endl;
        D = firstR(G);
        while (D != NULL) {
            cout << "Nama : " << infoD(D).nama << endl;
            cout << "ID : " << infoD(D).ID << endl;
            cout << "Peran : " << infoD(D).peran << endl;
            D = nextDev(D);
        }
        G = nextGame(G);
    }


    deleteRelation(G, D);

}
