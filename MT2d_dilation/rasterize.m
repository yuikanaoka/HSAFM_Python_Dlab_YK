function rXY = rasterize(raster, geometry1,minmax);
  #minmax <= 0: max value rasterize
  #        > 0: min value rasterize
  
  
  geometry = sortrows(geometry1);
  
  xstart = min(geometry(:,1));
  
  xend = max(geometry(:,1));
  
  L = length(raster);
  Lg = length(geometry);
  istart = 0;
  iend = 0;
  flagvar = 1; 
  
  for i=1:L
    
    if((raster(i)>xstart) && (flagvar == 1))
      istart = i
      flagvar = 0;
    endif
    
    if((raster(i)>xend))
      iend = i
      break;
    endif
    
  endfor
  
  y = zeros(iend-istart,1);
  x = zeros(iend-istart,1);
  
  raster_mag = Lg/(iend-istart)
  
  
  j0 = 0;
  for i=1:iend-istart-1
    
    j=1;
    while((geometry(j+j0,1) < raster(istart+i)))
      j++;
    endwhile
    
    if (minmax <= 0)
      y(i) = max(geometry(j0+1:j0+j,2));
    else
      y(i) = min(geometry(j0+1:j0+j,2));
    endif
    
    #x(i) = raster(istart+i);
    
    if ((j0 + j -1) < Lg)
      j0 += j-1;
    endif

  endfor
  
  if (minmax <= 0)
      y(i+1) = max(geometry(j0:Lg,2));
    else
      y(i+1) = min(geometry(j0:Lg,2));
  endif
  
  #x(i+1) = raster(istart+i+1);
  #plot(geometry(j0:Lg,1),geometry(j0:Lg,2),'.')
  #pause
  
  x = raster(istart:iend-1);
  
  rXY = [x',y];
  
endfunction
