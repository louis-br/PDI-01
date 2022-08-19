#===============================================================================
# Exemplo: segmentação de uma imagem em escala de cinza.
#-------------------------------------------------------------------------------
# Autor: Bogdan T. Nassu
# Universidade Tecnológica Federal do Paraná
#===============================================================================

import sys
import timeit
import numpy as np
import cv2

#===============================================================================

INPUT_IMAGE =  'arroz.bmp'

# TODO: ajuste estes parâmetros!
NEGATIVO = False
THRESHOLD = 0.8
ALTURA_MIN = 5
LARGURA_MIN = 5
N_PIXELS_MIN = 25

#===============================================================================

def binariza (img, threshold):
    ''' Binarização simples por limiarização.

Parâmetros: img: imagem de entrada. Se tiver mais que 1 canal, binariza cada
              canal independentemente.
            threshold: limiar.
            
Valor de retorno: versão binarizada da img_in.'''

    # TODO: escreva o código desta função.
    # Dica/desafio: usando a função np.where, dá para fazer a binarização muito
    # rapidamente, e com apenas uma linha de código!

    return np.where(img > THRESHOLD, -1, 0)

#-------------------------------------------------------------------------------

def inunda(rotulo, img, x0, y0, largura_img, altura_img, retangulo: dict):
    '''Flood fill recursivo. '''
    if x0 == -1 or x0 == largura_img - 1 or y0 == -1 or y0 == altura_img - 1 or img[y0][x0] != -1:
        return 0

    retangulo['L'] = min(retangulo['L'], x0)
    retangulo['R'] = max(retangulo['R'], x0)
    retangulo['T'] = min(retangulo['T'], y0)
    retangulo['B'] = max(retangulo['B'], y0)

    img[y0][x0] = rotulo

    n_pixels = 1
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        n_pixels += inunda(rotulo, img, x0 + dx, y0 + dy, largura_img, altura_img, retangulo)

    return n_pixels

def rotula (img, largura_min, altura_min, n_pixels_min):
    '''Rotulagem usando flood fill. Marca os objetos da imagem com os valores
[0.1,0.2,etc].

Parâmetros: img: imagem de entrada E saída.
            largura_min: descarta componentes com largura menor que esta.
            altura_min: descarta componentes com altura menor que esta.
            n_pixels_min: descarta componentes com menos pixels que isso.

Valor de retorno: uma lista, onde cada item é um vetor associativo (dictionary)
com os seguintes campos:

'label': rótulo do componente.
'n_pixels': número de pixels do componente.
'T', 'L', 'B', 'R': coordenadas do retângulo envolvente de um componente conexo,
respectivamente: topo, esquerda, baixo e direita.'''

    # TODO: escreva esta função.
    # Use a abordagem com flood fill recursivo.

    solucoes = []
    altura = len(img)
    largura = len(img[0])
    rotulo = 0.1

    for y in range(altura):
        for x in range(largura):
            if img[y][x] == -1:
                retangulo = {
                    'label': rotulo,
                    'n_pixels': 0,
                    'L': x,
                    'R': x,
                    'T': y,
                    'B': y
                }
                n_pixels = inunda(rotulo, img, x, y, largura, altura, retangulo)
                retangulo['n_pixels'] = n_pixels
                if n_pixels > n_pixels_min and retangulo['R'] - retangulo['L'] >= largura_min and retangulo['B'] - retangulo['T'] >= altura_min:
                    solucoes.append(retangulo)
                rotulo += 0.1
    
    return solucoes

#===============================================================================

def main ():

    # Abre a imagem em escala de cinza.
    img = cv2.imread (INPUT_IMAGE, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print ('Erro abrindo a imagem.\n')
        sys.exit ()

    # É uma boa prática manter o shape com 3 valores, independente da imagem ser
    # colorida ou não. Também já convertemos para float32.
    img = img.reshape ((img.shape [0], img.shape [1], 1))
    img = img.astype (np.float32) / 255

    # Mantém uma cópia colorida para desenhar a saída.
    img_out = cv2.cvtColor (img, cv2.COLOR_GRAY2BGR)

    # Segmenta a imagem.
    if NEGATIVO:
        img = 1 - img
    img = binariza (img, THRESHOLD)
    #cv2.imshow ('01 - binarizada', img)
    cv2.imwrite ('01 - binarizada.png', img*-255)

    start_time = timeit.default_timer ()
    componentes = rotula (img, LARGURA_MIN, ALTURA_MIN, N_PIXELS_MIN)
    n_componentes = len (componentes)
    print ('Tempo: %f' % (timeit.default_timer () - start_time))
    print ('%d componentes detectados.' % n_componentes)

    # Mostra os objetos encontrados.
    for c in componentes:
        cv2.rectangle (img_out, (c ['L'], c ['T']), (c ['R'], c ['B']), (0,0,1))

    #cv2.imshow ('02 - out', img_out)
    cv2.imwrite ('02 - out.png', img_out*255)
    #cv2.waitKey ()
    cv2.destroyAllWindows ()


if __name__ == '__main__':
    main ()

#===============================================================================
