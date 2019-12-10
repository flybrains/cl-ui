import numpy as np
import cv2
import os

def convert_canvas_to_bitmap(canvas):
    label = QLabel()
    pixmap = QPixmap('path_to_your_image')
    label.setPixmap(pixmap)

    height, width, channel = cvImg.shape
    bytesPerLine = 3 * width
    qImg = QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888)

def load_canvas(canvas_address):
    canvas = np.load(canvas_address)
    return canvas

def save_canvas(canvas, canvas_address):
    np.save(canvas, canvas_address)
    return None

def cache_canvas_data(canvas, revision):
    np.save(os.path.join(os.getcwd(), 'canvas_data', "{}.npy".format(revision)), canvas)

class Canvas(object):
    def __init__(self, w=1000, h=1000, module=False):
        self.w = w
        self.h = h
        self.airchannel = 255*np.ones((h, w), dtype=np.int16)
        self.channel1 = np.zeros((h, w), dtype=np.int16)
        self.channel2 = np.zeros((h, w), dtype=np.int16)
        self.resolution = 1
        self.revision = 1
        self.canvas = self.build_canvas()
        if module==False:
            cache_canvas_data(self.canvas, self.revision)
        else:
            pass

    def build_canvas(self):
        self.canvas = np.zeros((self.h, self.w, 3))
        self.canvas[:,:,0] = self.airchannel
        self.canvas[:,:,1] = self.channel1
        self.canvas[:,:,2] = self.channel2
        self.canvas = self.canvas.astype(np.uint8)
        return self.canvas

    def add_circular_gradient(self, x, y, r, max, min, channel):
        patch = np.zeros((2*r, 2*r))
        lowlimitx = x-r
        highlimitx = x+r
        lowlimity = y-r
        highlimity = y+r

        x_axis = np.linspace(-1, 1, 2*r)[:, None]
        y_axis = np.linspace(-1, 1, 2*r)[None, :]
        patch = (1-np.sqrt(x_axis ** 2 + y_axis ** 2))*255

        center = np.array([r,r])
        progCount = 0
        for i in range(2*r):
            for j in range(2*r):
                dist = np.linalg.norm(np.array([i,j]) - center)
                if dist >= r-1:
                    patch[i,j] = 0.

                self.progBarValue = int(100*(progCount/2*r))
                progCount+=1

        patch = patch.astype(np.int16)

        # Edge Handling
        if (x-r)<0:
            patch = patch[:,(r-x):]
            lowlimitx = 0
        if (y-r)<0:
            patch = patch[(r-y):,:]
            lowlimity = 0

        if (x+r)>self.w:
            patch = patch[:,:-(r-(self.w-x))]
            highlimitx = self.w
        if (y+r)>self.h:
            patch = patch[:-(r-(self.h-y)),:]
            highlimity = self.h

        if channel=='1':
            self.channel1[lowlimity:highlimity, lowlimitx:highlimitx] += patch[:,:]
        if channel=='2':
            self.channel2[lowlimity:highlimity, lowlimitx:highlimitx] += patch[:,:]

    def rollback_canvas(self):
        if self.revision > 1:
            temp = np.load(os.path.join(os.getcwd(), 'canvas_data', "{}.npy".format(self.revision-1)))
            self.airchannel = temp[:,:,0].astype(np.int16)
            self.channel1 = temp[:,:,1].astype(np.int16)
            self.channel2 = temp[:,:,2].astype(np.int16)
            self.canvas = self.build_canvas()
            self.revision -= 1
        return self.canvas

    def add_square_gradient(self, x, y, w, h, max, min, channel, maxat='Top'):

        if maxat=='Top':
            strand = np.linspace(max, min, num=h)
            tup = tuple([strand for i in range(w)])
            layer = np.column_stack(tup)
        if maxat=='Bottom':
            strand = np.linspace(min, max, num=h)
            tup = tuple([strand for i in range(w)])
            layer = np.column_stack(tup)
        if maxat=='Left':
            strand = np.linspace(max, min, num=w)
            tup = tuple([strand for i in range(h)])
            layer = np.row_stack(tup)
        if maxat=='Right':
            strand = np.linspace(min, max, num=w)
            tup = tuple([strand for i in range(h)])
            layer = np.row_stack(tup)

        # Replace canvas patch with gradient
        layer = layer.astype(np.int16)

        if channel=='1':
            self.channel1[y:(y+h), x:(x+w)] += layer[:,:]

        if channel=='2':
            self.channel2[y:(y+h), x:(x+w)] += layer[:,:]


    def check_and_correct_overlap(self):

        composite = np.add(self.channel1, self.channel2)
        problem_row = list(np.where(composite>255)[0])
        problem_col = list(np.where(composite>255)[1])
        problem_coords = [[problem_row[i], problem_col[i]] for i in range(len(problem_row))]

        for point in problem_coords:
            sum = self.channel1[point[0], point[1]]+self.channel2[point[0], point[1]]

            ch1_val = int((self.channel1[point[0], point[1]]/sum)*255)
            ch2_val = int((self.channel2[point[0], point[1]]/sum)*255)

            self.channel1[(point[0]),(point[1])] = ch1_val
            self.channel2[(point[0]),(point[1])] = ch2_val

        self.airchannel = 255*np.ones(self.channel1.shape) - (self.channel1 + self.channel2)

        # self.build_canvas()

        self.revision += 1
        self.canvas = self.build_canvas()
        cache_canvas_data(self.canvas, self.revision)


        return None

if __name__ == "__main__":
    canvas = Canvas(600,600)
    canvas.add_square_gradient(200, 0, 200, 600, 255, 0, 1, maxat='top')
    canvas.add_circular_gradient(400, 400, 100, 255, 0, 2)
    canvas.add_circular_gradient(200, 400, 100, 255, 0, 1)

    canvas.check_and_correct_overlap()
    cv2.imshow('grad1', canvas.canvas)
    cv2.waitKey(0)








#
