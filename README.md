## RenderDoc for Game data
This repo aims to acquire data from commerical games for various vision tasks whose data is difficulty to colloect. Before the start, please get familiar with the great game debugging tool [RenderDoc](https://github.com/baldurk/renderdoc).

<!--It is still under construction and lacks of some instructions and descriptions.-->

## What can you get
With this codebase, you can get various intermediate outputs of the rendering pipeline of a game, including depth, meshes and textures. Below are some examples from the commercial game GTAV (Grand Theft Auto V). Note that Rockstar Games, the publisher of GTAV, allows non-commerical use of footage from the game as long as certain conditions are met. See the [policy](https://support.rockstargames.com/articles/200153756/Policy-on-posting-copyrighted-Rockstar-Games-material).

### Various info in G-Buffer
You may get the diffuse map, normal map, specular map, irradiance map and depth map as follows.

|<img src="https://github.com/xiaofeng94/renderdoc_for_game_data/blob/v1.x/docs/imgs/outputs/rgb_resized.png" width="300"/>|<img src="https://github.com/xiaofeng94/renderdoc_for_game_data/blob/v1.x/docs/imgs/outputs/depth.png" width="300"/>|<img src="https://github.com/xiaofeng94/renderdoc_for_game_data/blob/v1.x/docs/imgs/outputs/difusse_resized.png" width="300" />|
|:---:|:---:|:---:|
|Final Output|Depth Map|Diffuse Map|
|<img src="https://github.com/xiaofeng94/renderdoc_for_game_data/blob/v1.x/docs/imgs/outputs/noraml_resized.png" width="300"/>|<img src="https://github.com/xiaofeng94/renderdoc_for_game_data/blob/v1.x/docs/imgs/outputs/irradiance_resized.png" width="300"/>|<img src="https://github.com/xiaofeng94/renderdoc_for_game_data/blob/v1.x/docs/imgs/outputs/specular_resized.png" width="300"/>|
|Normal Map|Irradiance Map|Specular Map|


### HDR and LDR image pairs
For someone who are interested in data-driven tone mapping and reverse tone mapping, it is a good choice to get HDR and LDR image pairs from the game.

|<img src="https://github.com/xiaofeng94/renderdoc_for_game_data/blob/v1.x/docs/imgs/outputs/rgb_resized.png" width="500"/>|<img src="https://github.com/xiaofeng94/renderdoc_for_game_data/blob/v1.x/docs/imgs/outputs/hdr_resized.png" width="500"/>|
|:---:|:---:|
|LDR Output|HDR Output|

### Semantic label
With mesh data and their various coordinates, you can even get the masks for amodal isntance semantic segementation where ostackled parts of the object should be labeled in the mask.

|<img src="https://github.com/xiaofeng94/renderdoc_for_game_data/blob/v1.x/docs/imgs/outputs/rgb_resized.png" width="500"/>|<img src="https://github.com/xiaofeng94/renderdoc_for_game_data/blob/v1.x/docs/imgs/outputs/mask_image.png" width="500"/>|
|:---:|:---:|
|Original Image|Amodel Mask|


### Foggy image simulation
With images and corresponding depth, you can get clear and foggy image pairs to faciliate your defogging researches.

|<img src="https://github.com/xiaofeng94/renderdoc_for_game_data/blob/v1.x/docs/imgs/outputs/rgb16333.png" width="500"/>|<img src="https://github.com/xiaofeng94/renderdoc_for_game_data/blob/v1.x/docs/imgs/outputs/fog16333.png" width="500"/>|
|:---:|:---:|
|Original Image|Simulated Foggy Image|
|<img src="https://github.com/xiaofeng94/renderdoc_for_game_data/blob/v1.x/docs/imgs/outputs/rgb44472.png" width="500"/>|<img src="https://github.com/xiaofeng94/renderdoc_for_game_data/blob/v1.x/docs/imgs/outputs/dust44472.png" width="500"/>|
|Original Image|Simulated Dust Image|

## Customization on your own
To begain with, you should get to know the rendering pipeline of your target game. For GTAV, you may find useful information in this [Link](http://www.adriancourreges.com/blog/2015/11/02/gta-v-graphics-study/). Then, compile the RenderDoc. Since I have just modified functions of capture and saving to save the depth maps, if you don't need those you may use the original RenderDoc. After that, capture frames you need. Finally, run the processing code in scripts/python in cmd (not the shell of RenderDoc).

Run `extract_data_for_GTA5.py` to get LDR, HDR, and depth maps. You may modify the variables `log_file_root` and `save_roots` on your own settings. If something's wrong with `capAPIForGTAV.py`, there may be a update in the rendering pipeline. In this case, you should locate the required data in the pipeline using the GUI of RenderDoc and modify the code accordingly. If you need helps, feel free to drop a email to 1731558@tongji.edu.cn.
