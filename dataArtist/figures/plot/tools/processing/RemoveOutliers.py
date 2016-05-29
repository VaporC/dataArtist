import numpy as np

from dataArtist.widgets.Tool import Tool



class RemoveOutliers(Tool):
    '''
    Remove outlier points from all plots
    Algorithm:
    * calc all plot gradients
    * sort the gradients in a histogram
    * get all gradients with have a histogram density smaller than the threshold
    * exclude values of the corresponding gradients
    '''
    icon = 'outliers.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)

        pa = self.setParameterMenu() 

        self.pMove = pa.addChild({
            'name':'Move outliers to new display',
            'type':'bool',
            'value':False}) 

        self.pThreshold = pa.addChild({
            'name':'Density minimum',
            'type':'float',
            'value':0.05,
            'limits':[0,1]}) 
        self.pGlobal = self.pThreshold.addChild({
            'name':'Global',
            'type':'bool',
            'value':True}) 


    def activate(self):
        self._back = []
        t = self.pThreshold.value()
        outlier_curves = []
        plot_labels = []
        
        if not self.pGlobal.value():            
            #THRESHOLD NEW FOR EVERY CURVE
            for curve in self.display.widget.curves:
                
                x,y = curve.xData, curve.yData
                self._back.append((x,y))
                #build a list of all gradients [excluding the first position]
                m = np.diff(y) / np.diff(x)
                #sort the gradients in a histogram
                hist, bin_edges = np.histogram(m, density=True)
                #normalise the histogram, so that hist.sum()=1
                hist*=np.diff(bin_edges)
                #build a False array
                outliers = np.zeros(shape=len(x), dtype=bool)
                for n,h in enumerate(hist):
                    if h < t:
                        #if m in outier range: add its index to outliers
                        outliers[1:] += np.logical_and(bin_edges[n] <= m, m <= bin_edges[n+1])
                        
                inliers = np.logical_not(outliers)
                curve.setData(x[inliers],y[inliers])  
                
                if self.pMove.value() and outliers.any():
                    plot_labels.append(curve.label.text)
                    outlier_curves.append((x[outliers], y[outliers]))
        else:
            #ALMOST SAME AS ABOTH BUT m IS COLLECTED FROM ALL CURVES FIRST
            m = []
            for curve in self.display.widget.curves:
                
                x,y = curve.xData, curve.yData
                self._back.append((x,y))
                #build a list of all gradients [excluding the first position]
                m.append(np.diff(y) / np.diff(x))
            
            m = np.array(m).flatten()
            #sort the gradients in a histogram
            hist, bin_edges = np.histogram(m, density=True)
            #normalise the histogram, so that hist.sum()=1
            hist*=np.diff(bin_edges)
            i = 0
            j = 0
            for curve in self.display.widget.curves:
                x,y = curve.xData, curve.yData

                #build a False array
                outliers = np.zeros(shape=len(x), dtype=bool)
                j += len(x)-1
                #get gradients for that curve from all gradients:
                mi = m[i:j]
                i = j
                for n,h in enumerate(hist):
                    if h < t:
                        #if m in outier range: add its index to outliers
                        outliers[1:] += np.logical_and(bin_edges[n] <= mi, 
                                                       mi <= bin_edges[n+1])
                        
                inliers = np.logical_not(outliers)
                
                curve.setData(x[inliers],y[inliers])  
                
                if self.pMove.value() and outliers.any():
                    plot_labels.append(curve.label.text)
                    outlier_curves.append((x[outliers], y[outliers]))
            
        if len(plot_labels):
            self.display.workspace.addDisplay(
                    origin=self.display,
                    data=outlier_curves, 
                    names=plot_labels,
                    title='Outliers') 
                  

    def deactivate(self):
        for curve, b in zip(self.display.widget.curves, self._back):
            curve.setData(b[0],b[1])   
  