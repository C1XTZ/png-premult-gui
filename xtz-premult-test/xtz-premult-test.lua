local originalWhite, originalBlack = './images/test_w.png', './images/test_b.png'
local premultipliedWhite, premultipliedBlack = './images/premult/test_w.png', './images/premult/test_b.png'
local appPath = '/apps/lua/xtz-premult-test'
local originalString, premultipliedString = 'Original', 'Converted'
local fontSize = 36
local defaultFont = ui.DWriteFont('default')

local function imageCheckText(path)
    local fullPath = appPath .. path:sub(2)
    ui.dwriteText(fullPath, fontSize, ui.isImageReady(path) and rgbm.colors.green or rgbm.colors.red)
end

function script.windowMain()
    if ui.isImageReady(originalWhite) and ui.isImageReady(originalBlack) and ui.isImageReady(premultipliedWhite) and ui.isImageReady(premultipliedBlack) then
        ui.setCursorY(60)
        local imgSize = ui.imageSize(originalWhite) / 14
        ui.image(originalBlack, imgSize)
        ui.sameLine()
        ui.beginPremultipliedAlphaTexture()
        ui.image(premultipliedBlack, imgSize)
        ui.endPremultipliedAlphaTexture()
        ui.image(originalWhite, imgSize)
        ui.sameLine()
        ui.beginPremultipliedAlphaTexture()
        ui.image(premultipliedWhite, imgSize)
        ui.endPremultipliedAlphaTexture()
        ui.pushDWriteFont(defaultFont)
        local w = ui.windowContentSize().x
        ui.beginOutline()
        ui.dwriteDrawText(originalString, fontSize, vec2(w * 0.25 - ui.measureDWriteText('Original', fontSize).x * 0.5, 15), rgbm.colors.white)
        ui.dwriteDrawText(premultipliedString, fontSize, vec2(w * 0.75 - ui.measureDWriteText('Premultiplied', fontSize).x * 0.5, 15), rgbm.colors.white)
        ui.endOutline(rgbm.colors.black, 0.5)
        ui.popDWriteFont()
    else
        ui.pushDWriteFont(defaultFont)
        ui.beginOutline()
        ui.dwriteText('Images unavailable.', fontSize, rgbm.colors.white)
        ui.dwriteText('You make sure you have the following files:', fontSize, rgbm.colors.white)
        imageCheckText(originalBlack)
        imageCheckText(originalWhite)
        imageCheckText(premultipliedBlack)
        imageCheckText(premultipliedWhite)
        ui.endOutline(rgbm.colors.black, 0.5)
        ui.popDWriteFont()
    end
end
