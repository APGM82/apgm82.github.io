import AppKit

// Póster vertical 9:16 para la web. uso: swift poster.swift <salida.png>
let W = 720.0, H = 1280.0
let iconPath = "/Users/apgm/Developer/ManaMTGArchive-KMP/iosApp/iosApp/Assets.xcassets/AppIcon.appiconset/icon-1024.png"
let outPath = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "poster.png"

let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(W), pixelsHigh: Int(H),
                           bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                           colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
let ctx = NSGraphicsContext.current!.cgContext

func rgb(_ r: Int, _ g: Int, _ b: Int, _ a: Double = 1) -> NSColor {
    NSColor(srgbRed: Double(r)/255, green: Double(g)/255, blue: Double(b)/255, alpha: a)
}

// fondo: degradado vertical navy -> púrpura -> navy
NSGradient(colors: [rgb(9, 12, 42), rgb(40, 21, 82), rgb(11, 16, 52)],
           atLocations: [0, 0.5, 1], colorSpace: .sRGB)!
    .draw(in: NSRect(x: 0, y: 0, width: W, height: H), angle: 70)

// resplandor tras el icono (parte alta)
NSGradient(colors: [rgb(140, 90, 220, 0.5), rgb(140, 90, 220, 0)], atLocations: [0, 1], colorSpace: .sRGB)!
    .draw(fromCenter: NSPoint(x: 360, y: 1040), radius: 0,
          toCenter: NSPoint(x: 360, y: 1040), radius: 380, options: [])

// icono centrado arriba
let icon = NSImage(contentsOfFile: iconPath)!
let side = 300.0
let iconRect = NSRect(x: (W - side)/2, y: 900, width: side, height: side)
ctx.saveGState()
ctx.setShadow(offset: CGSize(width: 0, height: -12), blur: 40, color: rgb(0, 0, 0, 0.65).cgColor)
let clip = NSBezierPath(roundedRect: iconRect, xRadius: side * 0.22, yRadius: side * 0.22)
clip.fill()
ctx.restoreGState()
ctx.saveGState()
clip.addClip()
icon.draw(in: iconRect)
ctx.restoreGState()
rgb(232, 199, 122, 0.35).setStroke(); clip.lineWidth = 3; clip.stroke()

// texto centrado
func drawC(_ s: String, y: Double, size: Double, weight: NSFont.Weight,
           color: NSColor, tracking: Double = 0) {
    let sh = NSShadow()
    sh.shadowColor = rgb(0, 0, 0, 0.8); sh.shadowBlurRadius = 12; sh.shadowOffset = NSSize(width: 0, height: -3)
    let attrs: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: size, weight: weight),
        .foregroundColor: color, .kern: tracking, .shadow: sh,
    ]
    let a = NSAttributedString(string: s, attributes: attrs)
    a.draw(at: NSPoint(x: (W - a.size().width)/2, y: y))
}

drawC("MANA", y: 800, size: 118, weight: .black, color: .white, tracking: 2)
drawC("MTG ARCHIVE", y: 742, size: 44, weight: .bold, color: rgb(232, 199, 122), tracking: 5)

// línea divisoria centrada
let dw = 300.0
rgb(232, 199, 122, 0.5).setFill()
NSBezierPath(rect: NSRect(x: (W - dw)/2, y: 724, width: dw, height: 3)).fill()

// subtítulo neutro
drawC("Magic: The Gathering", y: 250, size: 36, weight: .medium, color: rgb(214, 218, 245))

// pastillas de plataforma, centradas como grupo
func pillWidth(_ text: String) -> Double {
    let font = NSFont.systemFont(ofSize: 26, weight: .semibold)
    return (text as NSString).size(withAttributes: [.font: font]).width + 52
}
func pill(_ text: String, x: Double, y: Double) {
    let r = NSRect(x: x, y: y, width: pillWidth(text), height: 54)
    let p = NSBezierPath(roundedRect: r, xRadius: 27, yRadius: 27)
    rgb(255, 255, 255, 0.10).setFill(); p.fill()
    rgb(255, 255, 255, 0.30).setStroke(); p.lineWidth = 2; p.stroke()
    let attrs: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 26, weight: .semibold), .foregroundColor: NSColor.white,
    ]
    NSAttributedString(string: text, attributes: attrs).draw(at: NSPoint(x: x + 26, y: y + 13))
}
let gap = 18.0
let total = pillWidth("ANDROID") + gap + pillWidth("WINDOWS")
let startX = (W - total)/2
pill("ANDROID", x: startX, y: 120)
pill("WINDOWS", x: startX + pillWidth("ANDROID") + gap, y: 120)

NSGraphicsContext.restoreGraphicsState()
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: outPath))
print("OK -> \(outPath)")
