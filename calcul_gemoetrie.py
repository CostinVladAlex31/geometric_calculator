import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def arie_dreptunghi(lungime, latime):
    return lungime * latime

def perimetru_dreptunghi(lungime, latime):
    return 2 * (lungime + latime)

def arie_patrat(latura):
    return latura * latura

def perimetru_patrat(latura):
    return 4 * latura

def arie_cerc(raza):
    return math.pi * raza * raza

def perimetru_cerc(raza):
    return 2 * math.pi * raza

def arie_triunghi(a, b, c):
    s = (a + b + c) / 2
    return math.sqrt(s * (s - a) * (s - b) * (s - c))

def perimetru_triunghi(a, b, c):
    return a + b + c

def deseneza_dreptunghi(lungime, latime):
    figura, axa = plt.subplots(figsize=(8, 6))
    
    x = -lungime / 2
    y = -latime / 2
    
    dreptunghi = patches.Rectangle((x, y), lungime, latime, 
                                  fill=False, color='blue', linewidth=3)
    axa.add_patch(dreptunghi)
    
    spatiu = max(lungime, latime) * 0.3
    axa.set_xlim(x - spatiu, x + lungime + spatiu)
    axa.set_ylim(y - spatiu, y + latime + spatiu)
    axa.set_aspect('equal')
    axa.grid(True, alpha=0.3)
    
    arie = arie_dreptunghi(lungime, latime)
    perimetru = perimetru_dreptunghi(lungime, latime)
    
    plt.title(f'Dreptunghi {lungime}x{latime}\nArie: {arie:.3f} | Perimetru: {perimetru:.3f}')
    plt.show()

def deseneza_patrat(latura):
    figura, axa = plt.subplots(figsize=(8, 8))
    
    x = -latura / 2
    y = -latura / 2
    
    patrat = patches.Rectangle((x, y), latura, latura, 
                              fill=False, color='green', linewidth=3)
    axa.add_patch(patrat)
    
    spatiu = latura * 0.3
    axa.set_xlim(x - spatiu, x + latura + spatiu)
    axa.set_ylim(y - spatiu, y + latura + spatiu)
    axa.set_aspect('equal')
    axa.grid(True, alpha=0.3)
    
    arie = arie_patrat(latura)
    perimetru = perimetru_patrat(latura)
    
    plt.title(f'Patrat cu latura {latura}\nArie: {arie:.3f} | Perimetru: {perimetru:.3f}')
    plt.show()

def deseneza_cerc(raza):
    figura, axa = plt.subplots(figsize=(8, 8))
    
    cerc = plt.Circle((0, 0), raza, fill=False, color='red', linewidth=3)
    axa.add_patch(cerc)
    
    axa.plot([0, raza], [0, 0], 'r--', linewidth=2)
    axa.plot(0, 0, 'ro', markersize=8)
    
    spatiu = raza * 0.3
    axa.set_xlim(-raza - spatiu, raza + spatiu)
    axa.set_ylim(-raza - spatiu, raza + spatiu)
    axa.set_aspect('equal')
    axa.grid(True, alpha=0.3)
    
    arie = arie_cerc(raza)
    perimetru = perimetru_cerc(raza)
    
    plt.title(f'Cerc cu raza {raza}\nArie: {arie:.3f} | Perimetru: {perimetru:.3f}')
    plt.show()

def deseneza_triunghi(a, b, c):
    figura, axa = plt.subplots(figsize=(8, 8))
    
    latura_medie = (a + b + c) / 3
    inaltime = latura_medie * math.sqrt(3) / 2
    
    punctul_A = [0, 0]
    punctul_B = [latura_medie, 0]
    punctul_C = [latura_medie/2, inaltime]
    
    triunghi = patches.Polygon([punctul_A, punctul_B, punctul_C], fill=False, color='purple', linewidth=3)
    axa.add_patch(triunghi)
    
    axa.plot([punctul_A[0], punctul_B[0], punctul_C[0]], [punctul_A[1], punctul_B[1], punctul_C[1]], 'o', color='purple', markersize=8)
    
    axa.text(punctul_A[0]-0.3, punctul_A[1]-0.3, 'A', fontsize=14, ha='center')
    axa.text(punctul_B[0]+0.3, punctul_B[1]-0.3, 'B', fontsize=14, ha='center')
    axa.text(punctul_C[0], punctul_C[1]+0.3, 'C', fontsize=14, ha='center')
    
    spatiu = latura_medie * 0.2
    axa.set_xlim(-spatiu, latura_medie + spatiu)
    axa.set_ylim(-spatiu, inaltime + spatiu)
    axa.set_aspect('equal')
    axa.grid(True, alpha=0.3)
    
    arie = arie_triunghi(a, b, c)
    perimetru = perimetru_triunghi(a, b, c)
    
    plt.title(f'Triunghi {a}-{b}-{c}\nArie: {arie:.3f} | Perimetru: {perimetru:.3f}')
    plt.show()

def volum_cub(latura):
    return latura ** 3

def arie_totala_cub(latura):
    return 6 * latura ** 2

def volum_parallelpiped(lungime, latime, inaltime):
    return lungime * latime * inaltime

def arie_totala_parallelpiped(lungime, latime, inaltime):
    return 2 * (lungime * latime + lungime * inaltime + latime * inaltime)

def volum_sfera(raza):
    return (4/3) * math.pi * raza ** 3

def arie_sfera(raza):
    return 4 * math.pi * raza ** 2

def volum_prisma_triunghiulara(a, b, c, inaltime):
    arie_baza = arie_triunghi(a, b, c)
    return arie_baza * inaltime

def deseneza_cub_3d(latura):
    figura = plt.figure(figsize=(10, 8))
    axa = figura.add_subplot(111, projection='3d')
    
    valori = [-latura/2, latura/2]
    X, Y = np.meshgrid(valori, valori)
    
    axa.plot_surface(X, Y, np.ones_like(X) * latura/2, alpha=0.6, color='green')
    axa.plot_surface(X, Y, np.ones_like(X) * -latura/2, alpha=0.6, color='green')
    axa.plot_surface(X, np.ones_like(X) * latura/2, Y, alpha=0.6, color='green')
    axa.plot_surface(X, np.ones_like(X) * -latura/2, Y, alpha=0.6, color='green')
    axa.plot_surface(np.ones_like(X) * latura/2, X, Y, alpha=0.6, color='green')
    axa.plot_surface(np.ones_like(X) * -latura/2, X, Y, alpha=0.6, color='green')
    
    axa.set_xlim([-latura, latura])
    axa.set_ylim([-latura, latura])
    axa.set_zlim([-latura, latura])
    axa.set_xlabel('X')
    axa.set_ylabel('Y')
    axa.set_zlabel('Z')
    
    volum = volum_cub(latura)
    arie_totala = arie_totala_cub(latura)
    
    plt.title(f'Cub cu latura {latura}\nVolum: {volum:.3f} | Arie totala: {arie_totala:.3f}')
    plt.show()

def deseneza_parallelpiped_3d(lungime, latime, inaltime):
    figura = plt.figure(figsize=(10, 8))
    axa = figura.add_subplot(111, projection='3d')
    
    coordonate_x = [-lungime/2, lungime/2]
    coordonate_y = [-latime/2, latime/2]
    coordonate_z = [-inaltime/2, inaltime/2]
    
    X, Y = np.meshgrid(coordonate_x, coordonate_y)
    axa.plot_surface(X, Y, np.ones_like(X) * coordonate_z[1], alpha=0.6, color='red')
    axa.plot_surface(X, Y, np.ones_like(X) * coordonate_z[0], alpha=0.6, color='red')
    
    X, Z = np.meshgrid(coordonate_x, coordonate_z)
    axa.plot_surface(X, np.ones_like(X) * coordonate_y[1], Z, alpha=0.6, color='red')
    axa.plot_surface(X, np.ones_like(X) * coordonate_y[0], Z, alpha=0.6, color='red')
    
    Y, Z = np.meshgrid(coordonate_y, coordonate_z)
    axa.plot_surface(np.ones_like(Y) * coordonate_x[1], Y, Z, alpha=0.6, color='red')
    axa.plot_surface(np.ones_like(Y) * coordonate_x[0], Y, Z, alpha=0.6, color='red')
    
    dim_max = max(lungime, latime, inaltime)
    axa.set_xlim([-dim_max, dim_max])
    axa.set_ylim([-dim_max, dim_max])
    axa.set_zlim([-dim_max, dim_max])
    axa.set_xlabel('X')
    axa.set_ylabel('Y')
    axa.set_zlabel('Z')
    
    volum = volum_parallelpiped(lungime, latime, inaltime)
    arie_totala = arie_totala_parallelpiped(lungime, latime, inaltime)
    
    plt.title(f'Paralelpiped {lungime}x{latime}x{inaltime}\nVolum: {volum:.3f} | Arie totala: {arie_totala:.3f}')
    plt.show()

def deseneza_sfera_3d(raza):
    figura = plt.figure(figsize=(10, 8))
    axa = figura.add_subplot(111, projection='3d')
    
    unghi_u = np.linspace(0, 2 * np.pi, 50)
    unghi_v = np.linspace(0, np.pi, 50)
    
    coordonata_x = raza * np.outer(np.cos(unghi_u), np.sin(unghi_v))
    coordonata_y = raza * np.outer(np.sin(unghi_u), np.sin(unghi_v))
    coordonata_z = raza * np.outer(np.ones(np.size(unghi_u)), np.cos(unghi_v))
    
    axa.plot_surface(coordonata_x, coordonata_y, coordonata_z, alpha=0.6, color='red')
    axa.scatter([0], [0], [0], color='black', s=50)
    
    axa.set_xlim([-raza*1.2, raza*1.2])
    axa.set_ylim([-raza*1.2, raza*1.2])
    axa.set_zlim([-raza*1.2, raza*1.2])
    axa.set_xlabel('X')
    axa.set_ylabel('Y')
    axa.set_zlabel('Z')
    
    volum = volum_sfera(raza)
    arie_sfera_calculata = arie_sfera(raza)
    
    plt.title(f'Sfera cu raza {raza}\nVolum: {volum:.3f} | Arie: {arie_sfera_calculata:.3f}')
    plt.show()

def deseneza_prisma_3d(a, b, c, inaltime):
    figura = plt.figure(figsize=(10, 8))
    axa = figura.add_subplot(111, projection='3d')
    
    latura_medie = (a + b + c) / 3
    inaltime_triunghi = latura_medie * math.sqrt(3) / 2
    
    A_jos = [0, 0, -inaltime/2]
    B_jos = [latura_medie, 0, -inaltime/2]
    C_jos = [latura_medie/2, inaltime_triunghi, -inaltime/2]
    
    A_sus = [0, 0, inaltime/2]
    B_sus = [latura_medie, 0, inaltime/2]
    C_sus = [latura_medie/2, inaltime_triunghi, inaltime/2]
    
    fetele = [
        [A_jos, B_jos, C_jos],
        [A_sus, B_sus, C_sus],
        [A_jos, A_sus, B_sus, B_jos],
        [B_jos, B_sus, C_sus, C_jos],
        [C_jos, C_sus, A_sus, A_jos]
    ]
    
    poligon = Poly3DCollection(fetele, alpha=0.6, facecolor='pink', edgecolor='black')
    axa.add_collection3d(poligon)
    
    coordonata_maxima = max(latura_medie, inaltime_triunghi, inaltime)
    axa.set_xlim([0-coordonata_maxima*0.2, latura_medie+coordonata_maxima*0.2])
    axa.set_ylim([0-coordonata_maxima*0.2, inaltime_triunghi+coordonata_maxima*0.2])
    axa.set_zlim([-inaltime/2-coordonata_maxima*0.2, inaltime/2+coordonata_maxima*0.2])
    axa.set_xlabel('X')
    axa.set_ylabel('Y')
    axa.set_zlabel('Z')
    
    volum = volum_prisma_triunghiulara(a, b, c, inaltime)
    
    plt.title(f'Prisma triunghiulara\nBaza: {a}-{b}-{c}, Inaltime: {inaltime}\nVolum: {volum:.3f}')
    plt.show()

def meniu_3d():
    while True:
        print("\n--- VIZUALIZARE 3D ---")
        print("1. Cub 3D")
        print("2. Paralelpiped 3D") 
        print("3. Sfera 3D")
        print("4. Prisma triunghiulara 3D")
        print("0. Inapoi la meniul principal")
        
        alegere = input("\nAlege optiunea (0-4): ")
        
        if alegere == "1":
            latura = float(input("Latura cubului: "))
            print(f"Volum: {volum_cub(latura):.3f}")
            print(f"Arie totala: {arie_totala_cub(latura):.3f}")
            
            desenare = input("Vrei sa vezi desenul 3D? (Da/Nu): ")
            if desenare.lower() == 'da':
                deseneza_cub_3d(latura)
                
        elif alegere == "2":
            lungime = float(input("Lungime: "))
            latime = float(input("Latime: "))
            inaltime = float(input("Inaltime: "))
            
            print(f"Volum: {volum_parallelpiped(lungime, latime, inaltime):.3f}")
            print(f"Arie totala: {arie_totala_parallelpiped(lungime, latime, inaltime):.3f}")
            
            desenare = input("Vrei sa vezi desenul 3D? (Da/Nu): ")
            if desenare.lower() == 'da':
                deseneza_parallelpiped_3d(lungime, latime, inaltime)
                
        elif alegere == "3":
            raza = float(input("Raza sferei: "))
            
            print(f"Volum: {volum_sfera(raza):.3f}")
            print(f"Arie: {arie_sfera(raza):.3f}")
            
            desenare = input("Vrei sa vezi desenul 3D? (Da/Nu): ")
            if desenare.lower() == 'da':
                deseneza_sfera_3d(raza)
                
        elif alegere == "4":
            a = float(input("Latura a a bazei: "))
            b = float(input("Latura b a bazei: "))
            c = float(input("Latura c a bazei: "))
            inaltime = float(input("Inaltimea prismei: "))
            
            if (a + b > c) and (a + c > b) and (b + c > a):
                print(f"Volum: {volum_prisma_triunghiulara(a, b, c, inaltime):.3f}")
                
                desenare = input("Vrei sa vezi desenul 3D? (Da/Nu): ")
                if desenare.lower() == 'da':
                    deseneza_prisma_3d(a, b, c, inaltime)
            else:
                print("Nu se poate forma prisma cu aceste laturi pentru baza!")
                
        elif alegere == "0":
            break
        else:
            print("Optiune invalida!")

def meniu_principal():
    while True:
        print("\n= CALCULATOR GEOMETRIE ---")
        print("1. Dreptunghi")
        print("2. Patrat")
        print("3. Cerc") 
        print("4. Triunghi")
        print("5. Forme 3D")
        print("0. Iesire")
        
        alegere = input("\nAlege optiunea (0-5): ")
        
        if alegere == "1":
            lungime = float(input("Lungime: "))
            latime = float(input("Latime: "))
            
            arie = arie_dreptunghi(lungime, latime)
            perimetru = perimetru_dreptunghi(lungime, latime)
            
            print(f"Arie: {arie:.3f}")
            print(f"Perimetru: {perimetru:.3f}")
            
            desenare = input("Vrei sa vezi desenul? (Da/Nu): ")
            if desenare.lower() == 'da':
                deseneza_dreptunghi(lungime, latime)
                
        elif alegere == "2":
            latura = float(input("Latura: "))
            
            arie = arie_patrat(latura)
            perimetru = perimetru_patrat(latura)
            
            print(f"Arie: {arie:.3f}")
            print(f"Perimetru: {perimetru:.3f}")
            
            desenare = input("Vrei sa vezi desenul? (Da/Nu): ")
            if desenare.lower() == 'da':
                deseneza_patrat(latura)
                
        elif alegere == "3":
            raza = float(input("Raza: "))
            
            arie = arie_cerc(raza)
            perimetru = perimetru_cerc(raza)
            
            print(f"Arie: {arie:.3f}")
            print(f"Perimetru: {perimetru:.3f}")
            
            desenare = input("Vrei sa vezi desenul? (Da/Nu): ")
            if desenare.lower() == 'da':
                deseneza_cerc(raza)
                
        elif alegere == "4":
            a = float(input("Latura a: "))
            b = float(input("Latura b: "))
            c = float(input("Latura c: "))
            
            if (a + b > c) and (a + c > b) and (b + c > a):
                arie = arie_triunghi(a, b, c)
                perimetru = perimetru_triunghi(a, b, c)
                
                print(f"Arie: {arie:.3f}")
                print(f"Perimetru: {perimetru:.3f}")
                
                desenare = input("Vrei sa vezi desenul? (Da/Nu): ")
                if desenare.lower() == 'da':
                    deseneza_triunghi(a, b, c)
            else:
                print("Nu se poate forma triunghi cu aceste laturi!")
                
        elif alegere == "5":
            meniu_3d()
            
        elif alegere == "0":
            print("La revedere!")
            break
        else:
            print("Optiune invalida!")

if __name__ == "__main__":
    meniu_principal()
