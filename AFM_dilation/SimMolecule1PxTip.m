function heightmap = SimMolecule1PxTip(coordinates,grid_size)
  
  %print out everything during program execution
  more off;
  
  %calculate the minimum values of the coordinates...
  min_co = min(coordinates);
  %...and make sure they are set to zero
  coordinates(:,1) -= min_co(1);
  coordinates(:,2) -= min_co(2);
  coordinates(:,3) -= min_co(3);
  
  %get the number of the atoms
  Lc = length(coordinates(:,1));
  
  %get the maximum values of the coordinates...
  max_co = max(coordinates);
  %... and save the maximum values to new variables
  x_max = max_co(1)
  y_max = max_co(2)
  z_max = max_co(3)
  
  %set the number of pixels in x-direction according to the user input
  %the pixels in y-direction are calculated to fit the ration of x_max and y_max
  grid_size_x = grid_size;
  grid_size_y = ceil(grid_size*(y_max/x_max));
  
  %calculate how many nanometers one pixel is in x and y directions
  dx = x_max/grid_size_x;
  dy = y_max/grid_size_y;
  
  %designate the z-coordinates (height) to a new variable for convenience
  height_coords = coordinates(:,3);
  
  %allocate memory for the heightmap
  heightmap = zeros(grid_size_y,grid_size_x);
  
  %in these two for-loops the dilation of the molecule with a 1-px-tip is done;
  %the principle is the following: the maximum value (topmost atom) within a
  %pixel will give the height information for the tip, all atoms beneath area
  %meaningless for this calculation
  for iy = 1:grid_size_y
    
    for ix = 1:grid_size_x
      
      z_max_loc = 0;
      
      %create a boolean vector such that the entry is one if the coordinates 
      %are within the current pixel (ix,iy) (pixel dimensions are dx*dy) and
      %zero otherwise
      bol_vec = ((coordinates(:,1) >= dx*(ix-1)) .* (coordinates(:,1) < dx*ix)) .* ((coordinates(:,2) >= dy*(iy-1)) .* (coordinates(:,2) < dy*iy)) .* (coordinates(:,3) > z_max_loc);
      
      %multiply the boolean vector with the height coordinates...
      red_coord = bol_vec .* height_coords;
      %...and take the maximum value...
      z_max_loc = max(red_coord);
      
      %which is the height of the 1-px-topography heightmap at the 
      %position (ix,iy)
      heightmap(iy,ix) = z_max_loc;
    
    endfor
    
  endfor
  
  %save the heightmap in a text file 
  save('-ascii', 'heightmap1px.txt', 'heightmap')
  
  
end