# This is library for geometry analysis and operations
# for the Icw engine
import numpy as np


# Slicer function - for creating more dense segments fro analysis
def slicer(barGeometry):
    # Checking number of oryginal segments
    numberOfOrgSegments = len(barGeometry)
    newBarGeometry =[]

    #checking for the minimum segment lenght - 3th element - in all segments
    miniumumLenght = np.amin(barGeometry, axis=0)[2]

    #lets assume all subsegments as small as the minimum one
    desiredSegmentLenght = miniumumLenght

    for segment in range(0,numberOfOrgSegments):
        segmentLenght = barGeometry[segment][2]

        if segmentLenght >= 2*desiredSegmentLenght:
            # here we do sub segmentation process
            # First lets check how many time we need to divide  current segment
            segmentDivideFactor = int(segmentLenght / desiredSegmentLenght)

            #now lets calculate the new lenght
            segmentLenght = segmentLenght / segmentDivideFactor

            #and put required number of sub segments into geoemtry array
            for subsegment in range (0,segmentDivideFactor):
                newBarGeometry.append(np.array([barGeometry[segment][0],\
                barGeometry[segment][1],segmentLenght,barGeometry[segment][3]]))
        else:
            #here we return unchnged segment as its to short for subsegmentation
            newBarGeometry.append(barGeometry[segment])

    return np.array(newBarGeometry)
