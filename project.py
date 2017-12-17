import cv2
import numpy as np
import sys
import time
import math
from sudoku_puzzle import *
import pytesseract
from PIL import Image


dataset_size = 50
half = dataset_size // 2
sudoku_size = 9
top = int(dataset_size * 0.3)
bottom = int(dataset_size * 0.7)
crop_size = (bottom - top) ** 2
cut_size = dataset_size * sudoku_size
templete = np.array([np.array([0,0],np.float32), 
                        np.array([0,cut_size],np.float32),
                        np.array([cut_size,cut_size],np.float32),
                        np.array([cut_size,0],np.float32)])

def is_squre(vertex):
    a = math.sqrt((vertex[0][0][0] - vertex[1][0][0]) ** 2 + (vertex[0][0][1] - vertex[1][0][1]) ** 2)
    b = math.sqrt((vertex[1][0][0] - vertex[2][0][0]) ** 2 + (vertex[1][0][1] - vertex[2][0][1]) ** 2)
    c = math.sqrt((vertex[2][0][0] - vertex[3][0][0]) ** 2 + (vertex[2][0][1] - vertex[3][0][1]) ** 2)
    d = math.sqrt((vertex[3][0][0] - vertex[0][0][0]) ** 2 + (vertex[3][0][1] - vertex[0][0][1]) ** 2)
    
    if a/c > 1.2 or a/c < 0.8:
        return False
    if b/d > 1.2 or b/d < 0.8:
        return False
    return True

def find_puzzle(quadrangle, max_area):
    area = cv2.contourArea(max_area)
    result = []
    for rec in quadrangle:
        rec_area = cv2.contourArea(rec)
        if 0.75 <= rec_area/area <= 1.25:
            result.append(rec)
    return result


def center(vertex):
    x_pos = sum(vertex[i,0,0] for i in range(len(vertex))) // 4
    y_pos = sum(vertex[i,0,1] for i in range(len(vertex))) // 4
    for i in range(len(vertex)):
        x = vertex[i,0,0]
        y = vertex[i,0,1]
        if x <= x_pos and y <= y_pos:
            break
    return (vertex[i,0,:], vertex[(i+1)%4,0,:], vertex[(i+2)%4,0,:], vertex[(i+3)%4,0,:])

def cut(corner, img):
    transform = cv2.getPerspectiveTransform(corner, templete)
    return cv2.warpPerspective(img, transform, (cut_size,cut_size))

def recognition(img):
    for i in range(dataset_size):
        for j in range(dataset_size):
            dist_center = math.sqrt( (half - i)**2  + (half - j)**2)
            if dist_center > half * 0.85:
                img[i,j] = 255

    im,contour,hierarchy = cv2.findContours(img,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)

    bound_rect_max_size = 0
    for i in range(len(contour)):
        area = cv2.contourArea(contour[i])
        if 0.85*dataset_size*dataset_size > area > bound_rect_max_size:
            bound_rect_max_size = area
            x,y,w,h = cv2.boundingRect(contour[i])

    for i in range(dataset_size):
        for j in range(dataset_size):
            if j < x or j > x+w or i < y or i > y+h:
                img[i,j] = 255
    return pytesseract.image_to_string(Image.fromarray(img), config='-c tessedit_char_whitelist=123456789 -psm 10')


def getcell(warp_gray,x,y):
    cell = warp_gray[x*dataset_size:(x+1)*dataset_size,y*dataset_size:(y+1)*dataset_size]
    digits = cv2.adaptiveThreshold(cell, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 9)
    sub_square = digits[top:bottom, top:bottom]
    white = cv2.countNonZero(sub_square)
    porpotion = white / crop_size
    if porpotion > 0.87:
        return 0
    return recognition(digits)

def main():
    cur_window = 0

    size = cv2.getTextSize('0',cv2.FONT_HERSHEY_COMPLEX, 0.8, 2)[0]
    col = (dataset_size - size[0]) // 2
    row = (dataset_size - size[1]) // 2

    frame = cv2.imread("three.jpg")

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = img.shape
    img = cv2.GaussianBlur(img,(15,15),0)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 5)
    img = 255 - img


    im, contours, hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    puzzle_area = 0
    puzzle = np.ndarray(shape=(4,1,2),dtype=np.int32)
    quadrangle = []
    for j in range(len(contours)):
        ap = cv2.approxPolyDP(contours[j], 12, True)
        if not len(ap) == 4:
            continue
        elif not cv2.isContourConvex(ap):
            continue
        elif not is_squre(ap):
            continue
        elif cv2.contourArea(ap) < 9 * 9 * 14 * 14:
            pass
        else:
            quadrangle.append(ap)
            if puzzle_area < cv2.contourArea(ap):
                puzzle = ap
    quadrangle = find_puzzle(quadrangle,puzzle)
    

    for i in range(len(quadrangle)):
        puzzle = quadrangle[i]
        corner = center(puzzle)
        corner = np.array(corner, np.float32)
        warp = cut(corner, frame)
        warp_gray = cv2.cvtColor(warp, cv2.COLOR_BGR2GRAY)
        cv2.line(frame,(puzzle[0][0][0], puzzle[0][0][1]),(puzzle[1][0][0], puzzle[1][0][1]),(255, 0, 0), 2)
        cv2.line(frame,(puzzle[0][0][0], puzzle[0][0][1]),(puzzle[3][0][0], puzzle[3][0][1]),(255, 0, 0), 2)
        cv2.line(frame,(puzzle[3][0][0], puzzle[3][0][1]),(puzzle[2][0][0], puzzle[2][0][1]),(255, 0, 0), 2)
        cv2.line(frame,(puzzle[2][0][0], puzzle[2][0][1]),(puzzle[1][0][0], puzzle[1][0][1]),(255, 0, 0), 2)

        list_to_solve = []
        for i in range(9):
            l = []
            for j in range(9):
                l.append(int(getcell(warp_gray, i, j)))
            list_to_solve.append(l)
        
        puzzle_solver = SudokuPuzzle(list_to_solve)
        soln = puzzle_solver.solve()
        if not soln:
            result = [[0]*9]*9
        for c in range(9):
            for r in range(1,10):
                cv2.putText(warp, str(soln[r-1][c]), (c*dataset_size+col,r*dataset_size-row), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255,255,0), 2, cv2.LINE_AA)
        back_trans = cv2.getPerspectiveTransform(templete, corner)
        back = cv2.warpPerspective(warp, back_trans, (w,h))
        result_gray = cv2.cvtColor(back, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(result_gray, 20, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        frame = cv2.bitwise_and(frame,frame,mask=mask_inv)
        frame = cv2.add(frame, back)

    cv2.imshow("sudoku",frame)

    cv2.waitKey(0)
    cv2.destroyAllWindows()



if __name__ == "__main__":
    main()



