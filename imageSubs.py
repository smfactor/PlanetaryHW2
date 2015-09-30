from astropy.io import fits
from astropy.io import ascii
import numpy as np
from scipy.ndimage import interpolation as intp
import sys


def findStar(im, (xg, yg),r):
    '''
    Finds the flux weighted centroid of im in a circle centered at (xg, yg)
    with radius r.

    :param im:
    image array. convention is im[y,x].

    :param (xg, yg):
    initial guess for the center of the flux peak.

    :param r:
    radius to find the flux weighted centroid within (around (xg, yg)).
    '''
    x, y, tf = 0, 0, 0
    #sum flux and flux weighted coordinates
    for i in range(-r,r+1):
        for j in range(-r,r+1):
            if (np.sqrt((i)**2+(j)**2)<=6):
                f = im[yg+i,xg+j]
                tf += f
                x += f*i
                y += f*j

    #normalize by total flux
    x = x/tf
    y = y/tf
    return (x+xg, y+yg)

def register(ntargets, directory, fileNames, extraTxt, targets, positions, (xref, yref)):
    '''
    "Registers" images: shifts them all to the same position and rotates them 
    according to their PA then outputs the sum and median image of each target.
    NOTE: All arrays (fileNames, targest, positions) must be the same size.

    :param ntargets:
    number of targets in the data set. Target 0 is assumed to be acquisition images

    :param directory:
    directory to look for images in.

    :param fileNames:
    array of file names. Just the name, no directory information. Should all end in '.fits'.
    
    :param extraTxt:
    extra text to stick in before '.fits' (e.g. used for registering psf 
    subtracted images rather than regular callibrated images)

    :param targets:
    array of ints (0 to ntargets) corresponding to the target number. 0 is 
    assumed to be aquisition images.

    :param positions:
    array of the x-y positions of the star in eahc image to register on.

    :param (xref, yref):
    x-y position to register all images to (i.e. shift all images from the 
    coordinates given in :param positions: such that the star is now located 
    at :param (xref, yref):)
    '''

    print 'registering and stacking '+extraTxt
    n = np.size(targets)
    #loop over targets != 0
    for t in range(1,ntargets+1):
        reg = np.array([])
        rot = np.array([])
        for i in range(n):
            if targets[i]==t:
                #load image and header info, shift and rotate image, write file
                im = fits.getdata(directory+fileNames[i][:-4]+extraTxt+'fits')
                hdr = fits.getheader('calfits/'+fileNames[i])
                sim = intp.shift(im,[yref-positions['y'][i],xref-positions['x'][i]])
                fits.writeto('results/'+fileNames[i][:-4]+extraTxt+'reg.fits',sim)
                PA = hdr['PARANG']+hdr['ROTPPOSN']-hdr['EL']-hdr['INSTANGL']
                rim = intp.rotate(sim,-PA,reshape=False)

                #coalate registered and rotated images
                if reg.sum()==0:
                    reg=np.array([sim])
                    rot=np.array([rim])
                else:
                    reg= np.append(reg,[sim],axis=0)
                    rot = np.append(rot,[rim],axis=0)

                #progress bar
                percent = float(i) / n
                hashes = '#' * int(round(percent * 20))
                spaces = ' ' * (20 - len(hashes))
                sys.stdout.write("\rTarget {0}: Percent: [{1}] {2}%".format(t, hashes + spaces, int(round(percent * 100))))
                sys.stdout.flush()

        #sum and median shifted and rotated images and write files
        sumt= np.sum(reg,axis=0)
        fits.writeto('results/'+extraTxt+'target'+str(t)+'sum.fits', sumt)

        medt = np.median(reg,axis=0)
        fits.writeto('results/'+extraTxt+'target'+str(t)+'med.fits',medt)

        sumr = np.sum(rot,axis=0)
        fits.writeto('results/'+extraTxt+'target'+str(t)+'rotsum.fits',sumr)

        medr = np.median(rot,axis=0)
        fits.writeto('results/'+extraTxt+'target'+str(t)+'rotmed.fits',medr)
    sys.stdout.write("\n")

def findRatio(im,psf,mask): #(xc,yc),r,d):
    '''
    Finds the median scaling ratio between im and psf such that im - s*psf ~= 0

    :param im:
    science image

    :param psf:
    psf that needs to be scaled to :param im:

    :param mask:
    array of 1's and 0's to median over.
    '''
    ##old code using loops rather than numpy array operations
    #xs, ys = np.shape(im)
    #ratios = np.array([])
    #for i in range(xs):
    #    for j in range(ys):
    #        if (np.sqrt((i-xc)**2+(j-yc)**2)<r+d and np.sqrt((i-xc)**2+(j-yc)**2)>r):
    #            ratios = np.append(ratios,im[j,i]/psf[j,i])
    #return np.median(ratios)
    ratio = (im/psf)*mask
    return np.median(ratio[np.where(mask!=0)])
