function tip_map = MakeTip(tip_radius, tip_size, dx, dy)
  
  if (mod(tip_size,2) == 0)
    
    tip_size += 1;
    
  endif
  
  center_distance = (tip_size - 1)/2 + 1;
  
  tip_map = zeros(tip_size);
  
  for ix = 1:tip_size
    
    for iy = 1:tip_size
      
      tip_map(ix,iy) = (1/(2*tip_radius))*(((ix-center_distance)*dx)^2 + ((iy-center_distance)*dy)^2);
      
    endfor
    
  endfor
  
  
  %imshow(tip_map/max(max(tip_map)))
  
end