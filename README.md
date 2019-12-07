### In "Classification and mutation ---", they use 512x512 pixlel tiles  
### Without overlapping.  
### Whether to reserve the boudary tiles?  
### Omit those with over 50% backgrounds  

In article "Classification and mutation prediction from non–small cell lung cancer histopathology  
images using deep learning"  
They use:  
  + 1. they use 512x512 pixlel tiles  
  + 2. Without overlapping.  
  + 3. omit tiles with over 50% backgrounds(so it's possible that they have rejected the boundary pictures.  
  + 4. Inception-V3 architecture  
  + 5. Result od per tiles are aggregated to extract the heatmaps and the AUC statistics.  
    

Classification Method:  
  + 1. Average the probilities obtained by each tile.           --With AUC 0.990  
  + 2. Calculate the ratio of tiles positively classified.      --With AUC 0.993  
    
They may used two types of patches to train the model:  
  + 1. 20x magnification, with tile size 512x512(maybe)  
  + 1. 5x magnification, with tile size 512x512  

An impact of imbalanced data:  
  + TCGA images have significantly higher tumor content compared to the independent datasets,  
  + which will influence the generalizability of the model.  
  
For some "unknown" features, AUC on classifier on 5x-magnified tiles is mostly higher than the slides from 20x-magnified tiles.  