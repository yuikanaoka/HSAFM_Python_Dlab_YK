function DILATED_PROFILE = dilation(SUBSTRATE, TIP, SAMPLE)
  
  Lsa = length(SAMPLE);
  Lsu = length(SUBSTRATE);
  Lt = length(TIP);
  
  Lsa
  Lsu
  Lt
  
  step_size = (max(SUBSTRATE(:,1)) - min(SUBSTRATE(:,1)))/(Lsu-1)
  
  SUBSAM = SUBSTRATE;
  
  SUBSAM(Lsu/2-Lsa/2:Lsu/2+Lsa/2-1,2) = SAMPLE(:,2);
  
  TIP(:,1) -= min(TIP(:,1)) - min(SUBSAM(:,1));
  
  steps = Lsu - Lt;
  
  %DILATED_PROFILE = zeros(2,2);
  DILATED_PROFILE = zeros(steps,2);
  DILATED_PROFILE(:,1) = SUBSAM(floor(Lt/2):Lsu-ceil(Lt/2)-1,1);
  
  for i=1:steps  
    
    dH = min(TIP(:,2) - SUBSAM(i:Lt+i-1,2));
    
    %pause
    
    TIP(:,2) -= dH;
    
    [y,iy] = min(TIP(:,2));
    
    DILATED_PROFILE(i,1) = TIP(iy,1);
    DILATED_PROFILE(i,2) = TIP(iy,2);
    
    if (mod(i,10) == 0)
      %clf;
      %subplot(2,1,2)
      %plot(SUBSAM(:,1),SUBSAM(:,2),'-k', TIP(:,1),TIP(:,2),'-b', DILATED_PROFILE(:,1), DILATED_PROFILE(:,2), '-r');
      %axis([-40,40,-10,40],"equal");
      %drawnow();
    endif
    
    
    
    TIP(:,1) += step_size;
    
  endfor
  
  %clf;
  %subplot(2,1,2)
  %plot(SUBSAM(:,1),SUBSAM(:,2),'-k', TIP(:,1),TIP(:,2),'-b', DILATED_PROFILE(:,1), DILATED_PROFILE(:,2), '-r');
  %axis([-40,40,-10,40],"equal");
  %drawnow();
  
endfunction
