#ifndef GAMEPROJECT_H_INCLUDED
#define GAMEPROJECT_H_INCLUDED
#include <iostream>
using namespace std;
#define infoG(G) G->infoG
#define nextGame(G) G->nextGame
#define firstGame(Lg) Lg->firstGame
#define lastGame(Lg) Lg->lastGame
#define infoD(D) D->infoD
#define nextDev(D) D->nextDev
#define firsDevelop(Ld) Ld-firstDevelop
#define firstR(G) G->firstR

typedef struct projectGame infoGame;
typedef struct development infoDev;

struct projectGame{
    string kode, namaGame, genre, platform, deadline, server;
};
struct development {
    string nama, ID, peran;
};

typedef struct elmGame *adr_game;
typedef struct elmDev *adr_develop;

struct elmGame {
    infoGame infoG;
    adr_game nextGame;
    adr_develop firstR;
};

struct elmDev {
    infoDev infoD;
    adr_develop nextDev;
};

struct listGame {
    adr_game firstGame;
    adr_game lastGame;
};
struct listDev {
    adr_develop firstDevelop;
};

adr_game createGame(string kode, string namaGame, string genre, string platform, string deadline, string server);
void inserLastGame(listGame &Lg, adr_game G);
void addRelation(adr_game G, adr_develop D);
void deleteFirstGame(listGame &Lg, listDev &Ld);
adr_develop createKaryawan(string nama, string ID, string peran);
void insertFirstKaryawan(listDev &Ld, adr_develop D);
void deleteLastKaryawan(listDev &Ld, listGame &G);
void deleteRelation(adr_game &G, adr_develop &D);
void showGame(listGame &Lg);
void showKaryawan(listDev &Ld)


#endif // GAMEPROJECT_H_INCLUDED
