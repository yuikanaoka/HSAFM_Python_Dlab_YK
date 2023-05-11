function xyz = ReadCIF(filename)
  
  file = fopen(filename);
  
  i = 1;
  
  while !(feof(file))
    
      line = fgetl(file);
      
      if length(line) >= 12
        
        if (strcmp(line(1:4),'ATOM') || strcmp(line(1:6),'HETATM'))
          
          
          [x,y,z] = sscanf(line,"%*s%*[ ]%*i%*[ ]%*s%*[ ]%*s%*[ ]%*s%*[ ]%*s%*[ ]%*s%*[ ]%*i%*[ ]%*s%*[ ]%*s%*[ ]%f%*[ ]%f%*[ ]%f", "C");
          xyz(i,1:3) = [x,y,z];
          
          i++;
          
        endif
        
      endif
      
  endwhile
  
  fclose(file);
  
end