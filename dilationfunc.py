import config
import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import datetime




class dilationfunction:
    def __init__(self):
        print("dilationfunction")

#=========================
# create tip
#=========================
    def createtip(self):
        print("create tip")
        createtipstart=datetime.datetime.now()
        print ("create tip start time: "+str(createtipstart)) 
        

        z_off = (config.tipradius / 2) / math.tan(config.tipangle * math.pi / 180) ** 2
        r_crit=config.tipradius/math.tan(config.tipangle*math.pi/180)
        z_crit=r_crit/math.tan(config.tipangle*math.pi/180)-z_off

        if config.tipshape=="Paraboloid":
            i_xm=(1/config.dx)*math.sqrt(2*config.tipradius*(config.zcoordinate.max()-config.zcoordinate.min()))
            config.tipsize=2*math.ceil(i_xm)+1
            #print ("paraboloid")
        
        elif config.tipshape=="Cone":
            r_crit=config.tipradius/math.sqrt(1+math.tan(config.tipangle*math.pi/180)**2)
            z_crit=r_crit*math.tan(config.tipangle*math.pi/180)-z_off
            z_off=-config.tipradius+math.sqrt(config.tipradius**2-r_crit**2)+r_crit**2/math.sqrt(config.tipradius**2-r_crit**2)
            if z_crit>config.zcoordinate.max():
                i_xm=(1/config.dx)*math.sqrt(config.tipradius**2-(config.tipradius-(config.zcoordinate.max()-config.zcoordinate.min()))**2)
            else:
                i_xm=(1/config.dx)*((config.zcoordinate.max()-config.zcoordinate.min())+z_off)*math.tan(config.tipangle*math.pi/180)
            config.tipsize=2*math.ceil(i_xm)+1
        
                                
        config.tipsize_half=math.trunc(config.tipsize/2)+1

        if config.tipsize%2==0:
            config.tipsize=config.tipsize+1
        centerdistance=(config.tipsize-1)/2
        config.tipwave=np.zeros((config.tipsize,config.tipsize))

        #print (config.tipsize)

        if config.tipshape=="Paraboloid":
            for iy in range(0,config.tipsize):
                for ix in range(0,config.tipsize):
                    config.tipwave[iy][ix]=(1/(2*config.tipradius))*(((ix - centerdistance)*config.dx)**2 + ((iy - centerdistance)*config.dy)**2)
        elif config.tipshape=="Cone":
            curvewave=np.zeros((config.tipsize,config.tipsize))
            conewave=np.zeros((config.tipsize,config.tipsize))
            r_crit=config.tipradius/math.sqrt(1+math.tan(config.tipangle*math.pi/180)**2)
            z_off=-config.tipradius+math.sqrt(config.tipradius**2-r_crit**2)+r_crit**2/math.sqrt(config.tipradius**2-r_crit**2)
            for iy in range(0,config.tipsize):
                for ix in range(0,config.tipsize):
                    xpos=(ix - centerdistance)*config.dx
                    ypos=(iy - centerdistance)*config.dy
                    r_i=math.sqrt(xpos**2+ypos**2)
                    if r_i<=r_crit:
                        config.tipwave[iy][ix]=config.tipradius-math.sqrt(config.tipradius**2-r_i**2)
                    else:
                        config.tipwave[iy][ix]=r_i/math.tan(config.tipangle*math.pi/180)-z_off
                    

        createtipend=datetime.datetime.now()
        print ("create tip start time: "+str(createtipend)) 
        print ("create tip time: "+str(createtipend-createtipstart))
        
        #print (config.tipwave)
        # print (config.tipsize)
        # print (config.tipwave.shape)
        # print (type(config.tipwave))
        # tipwavex,tipwavey=np.indices(config.tipwave.shape)

        
        # figtip=plt.figure(num="Tip")
        # oneax=figtip.add_subplot(111, projection='3d')
        # oneax.plot_surface(tipwavex,tipwavey,config.tipwave)
        # #plt.imshow(config.tipwave)
        # plt.show(block=False)
        # plt.draw()

        

        

    #=========================
    # one pixel dilation
    #=========================
    def onepixeldilation(self):
        print ("one pixel dilation")
        onepixelstart=datetime.datetime.now()
        print ("one pixel dilation start time: "+str(onepixelstart))
        #config.onepixeldilation=np.zeros((config.pixelxdirection+2*config.tipsize, config.pixelydirection+2*config.tipsize))
        
        #make height map
        config.onepixeldilation=np.zeros((config.grid_sizex,config.grid_sizey))

        for iy in range(0,config.grid_sizey):
            for ix in range(0,config.grid_sizex):
                z_max=0
                bol_vec=(  (config.ycoordinate>=(iy-1)*config.dy) & (config.ycoordinate<(iy)*config.dy)& (config.xcoordinate>=(ix-1)*config.dx) & (config.xcoordinate<(ix)*config.dx)  &  (config.zcoordinate>(z_max)))
                red_coord = bol_vec*config.zcoordinate
                z_max=red_coord.max()
                config.onepixeldilation[ix][iy]=z_max

        onepixelend=datetime.datetime.now()
        print ("one pixel dilation end time: "+str(onepixelend))
        print ("one pixel dilation time: "+str(onepixelend-onepixelstart))
        # onepixelx, onepixely=np.indices(config.onepixeldilation.shape)
        # figonepixel=plt.figure(num="onepixel")
        # oneax=figonepixel.add_subplot(111, projection='3d')
        # oneax.scatter(onepixelx,onepixely,config.onepixeldilation)
        # oneax.set_xlabel('X axis')
        # oneax.set_ylabel('Y axis')
        # oneax.set_zlabel('Z axis')
        # plt.show(block=False)
        # plt.draw()

        # img_array=(config.onepixeldilation/config.onepixeldilation.max())*255
        # img_array=img_array.astype(np.uint8)
        # #img=Image.fromarray(img_array)
        # #img.save('dilation.png')
        # imgone=plt.figure(num="Simlated one pixel img")
        # imgax=imgone.add_subplot(111)
        # imgax.imshow(img_array)
        # plt.show(block=False)



    #=========================
    # make dilation
    #=========================
    def dilation(self):
        starttime = datetime.datetime.now()
        print ("Start time: " + str(starttime))
        config.xcoordinate=config.pdbplot['X']-config.pdbplot['X'].min()
        config.ycoordinate=config.pdbplot['Y']-config.pdbplot['Y'].min()
        config.zcoordinate=config.pdbplot['Z']-config.pdbplot['Z'].min()

        config.xcoordinate=config.xcoordinate/10
        config.ycoordinate=config.ycoordinate/10
        config.zcoordinate=config.zcoordinate/10

        #get the number of the atoms
        atomnumber=len(config.pdbplot)
        #set the number of pixels
        config.grid_sizex=config.pixelxdirection
        config.grid_sizey=math.ceil(config.pixelxdirection*(config.ycoordinate.max()/config.xcoordinate.max()))

        #set resolution nm/pixel
        config.dx=(config.xcoordinate.max())/config.grid_sizex
        config.dy=(config.ycoordinate.max())/config.grid_sizey
        
        self.onepixeldilation()
        #make tip
        self.createtip()
        #print("after create tip")
        #print (config.tipsize)
        #print (config.tipwave.shape)

        l_x=config.grid_sizex+2*config.tipsize
        l_y=config.grid_sizey+2*config.tipsize
        config.dilationborder=np.zeros((l_x,l_y))
        config.dilationborder[config.tipsize:l_x-config.tipsize,config.tipsize:l_y-config.tipsize]=config.onepixeldilation
        img_array_border=(config.dilationborder/config.dilationborder.max())*255
        img_array_border=img_array_border.astype(np.uint8)
        #img=Image.fromarray(img_array)
        #img.save('dilation.png')
        # imgborderfig=plt.figure(num="dilation border img")
        # imgborderax=imgborderfig.add_subplot(111)
        # imgborderax.imshow(img_array_border)
        # plt.show(block=False)

        config.dilation=np.zeros((l_x,l_y))
        #print (l_x)
        #print (l_y)


        #make dilation
        for ix in range(0,l_x-config.tipwave.shape[0]):
            for iy in range(0,l_y-config.tipwave.shape[1]):
                #print (iy)
                #print (iy+config.tipsize)

                #print(ix)
                # print(ix+config.tipsize)
                z_diffmap=config.dilationborder[ix:ix+config.tipsize,iy:iy+config.tipsize]-config.tipwave
                # print ("ok")
                # print(z_diffmap.shape)
                # print ("======")
                displacement=z_diffmap.max()
                config.dilation[ix+config.tipsize_half][iy+config.tipsize_half]=displacement
        
        #config.dilation=config.dilation/(config.dilation.max())
        #print ("type")
        #print(type(config.dilation))
        #config.dilation=config.dilation/10
        np.savetxt('dilation.csv', config.dilation, delimiter=',')
        

        #apply afm color map and save image 
        #self.makeDIcolor()
        #config.dilation_img=cv2.applyColorMap(config.dilation, config.DIcolor)
        #self.createtip()
        #one pixel dilation
        endtime = datetime.datetime.now()
        print ("End time: " + str(endtime))
        print ("Simulation time: " + str(endtime - starttime))
        self.dilation_display_update()
        plt.show(block=False)
        




        # dilationx, dilationy=np.indices(config.dilation.shape)
        # figdilation=plt.figure(num="dilation")
        # dilaax=figdilation.add_subplot(111, projection='3d')
        # dilaax.scatter(dilationx,dilationy,config.dilation)
        # dilaax.set_xlabel('X axis')
        # dilaax.set_ylabel('Y axis')
        # dilaax.set_zlabel('Z axis')
        # plt.show(block=False)
        # plt.draw()


