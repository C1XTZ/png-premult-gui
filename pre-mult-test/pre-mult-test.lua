local imgBlackNoPre = './test_b.png'
local imgBlackPreMult = './test_b_mult.png'
local imgWhiteNoPre = './test_w.png'
local imgWhitePreMult = './test_w_mult.png'
local imgsize = vec2(300, 300)

function script.windowMain(dt)
    ui.image(imgBlackNoPre, imgsize)

    ui.sameLine()
    
    ui.beginPremultipliedAlphaTexture()
    ui.image(imgBlackPreMult, imgsize)
    ui.endPremultipliedAlphaTexture()

    ui.image(imgWhiteNoPre, imgsize)

    ui.sameLine()
    
    ui.beginPremultipliedAlphaTexture()
    ui.image(imgWhitePreMult, imgsize)
    ui.endPremultipliedAlphaTexture()
end
