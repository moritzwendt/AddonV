



import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import QtQuick.Shapes

ApplicationWindow {
    id: root
    width: 1120
    height: 740
    minimumWidth: 940
    minimumHeight: 600
    visible: true
    flags: Qt.Window | Qt.FramelessWindowHint
    color: "transparent"
    title: "AddonV"

    property int currentPage: 0
    readonly property bool maximized: root.visibility === Window.Maximized


    FontLoader { id: fGeist;     source: "fonts/Geist.ttf" }
    FontLoader { id: fGeistMono; source: "fonts/GeistMono.ttf" }
    FontLoader { id: fSora;      source: "fonts/Sora.ttf" }


    QtObject {
        id: th

        readonly property string ui:   fGeist.status === FontLoader.Ready ? fGeist.name : "Segoe UI"
        readonly property string mono: fGeistMono.status === FontLoader.Ready ? fGeistMono.name : "Cascadia Mono"
        readonly property string disp: fSora.status === FontLoader.Ready ? fSora.name : "Segoe UI"

        readonly property color appBg: "#0b0c0d"
        readonly property color card: "#161719"
        readonly property color cardBorder: "#232527"
        readonly property color dropBg: "#141517"
        readonly property color dropDash: "#2c2f31"
        readonly property color innerBox: "#0e0f10"
        readonly property color innerBorder: "#202224"
        readonly property color divider: "#202224"
        readonly property color rowBorder: "#161719"
        readonly property color settingRowBorder: "#1a1b1d"
        readonly property color ghostBg: "#1b1d1f"
        readonly property color ghostBorder: "#26282c"
        readonly property color ghostText: "#cfd2d7"
        readonly property color textHi: "#ffffff"
        readonly property color text: "#e9eaec"
        readonly property color dim: "#9498a0"
        readonly property color mute: "#787c84"
        readonly property color faint: "#565a62"
        readonly property color lineNum: "#3c4049"
        readonly property color knobOff: "#2a2e35"
        readonly property color checkBorder: "#3a3f48"

        readonly property color accent: backend.accent
        readonly property color accentText: Qt.lighter(backend.accent, 1.35)

        readonly property color stActiveDot: "#40c787"
        readonly property color stActiveText: "#73dea4"
        readonly property color stDisabledDot: "#5d636c"
        readonly property color stDisabledText: "#8a9099"
        readonly property color stNotinDot: "#e9a03e"
        readonly property color stNotinText: "#fab45f"
        readonly property color stDupDot: "#f05653"
        readonly property color stDupText: "#ff7a73"
        readonly property color dangerText: "#f97770"
        readonly property color glyphOk: "#48cd8c"
        readonly property color glyphErr: "#f75d59"
        readonly property color glyphRun: "#6b7280"
        readonly property color tagInfo: "#8a9099"
        readonly property color tagEls: "#28c2be"
        readonly property color tagXml: "#a795ef"
        readonly property color closeHover: "#d73337"

        readonly property int rLg: 9
        readonly property int rMd: 8
        readonly property int rSm: 7
        readonly property int rBtn: 8
        readonly property int rIcon: 11
        readonly property int rBox: 8
    }


    QtObject {
        id: ico
        readonly property string install: "M228,144v64a12,12,0,0,1-12,12H40a12,12,0,0,1-12-12V144a12,12,0,0,1,24,0v52H204V144a12,12,0,0,1,24,0Zm-108.49,8.49a12,12,0,0,0,17,0l40-40a12,12,0,0,0-17-17L140,115V32a12,12,0,0,0-24,0v83L96.49,95.51a12,12,0,0,0-17,17Z"
        readonly property string packs: "M225.6,62.64l-88-48.17a19.91,19.91,0,0,0-19.2,0l-88,48.17A20,20,0,0,0,20,80.19v95.62a20,20,0,0,0,10.4,17.55l88,48.17a19.89,19.89,0,0,0,19.2,0l88-48.17A20,20,0,0,0,236,175.81V80.19A20,20,0,0,0,225.6,62.64ZM128,36.57,200,76,178.57,87.73l-72-39.42Zm0,78.83L56,76,81.56,62l72,39.41ZM44,96.79l72,39.4v76.67L44,173.44Zm96,116.07V136.19l24-13.13V152a12,12,0,0,0,24,0V109.92l24-13.13v76.65Z"
        readonly property string settings: "M128,76a52,52,0,1,0,52,52A52.06,52.06,0,0,0,128,76Zm0,80a28,28,0,1,1,28-28A28,28,0,0,1,128,156Zm92-27.21v-1.58l14-17.51a12,12,0,0,0,2.23-10.59A111.75,111.75,0,0,0,225,71.89,12,12,0,0,0,215.89,66L193.61,63.5l-1.11-1.11L190,40.1A12,12,0,0,0,184.11,31a111.67,111.67,0,0,0-27.23-11.27A12,12,0,0,0,146.3,22L128.79,36h-1.58L109.7,22a12,12,0,0,0-10.59-2.23A111.75,111.75,0,0,0,71.89,31.05,12,12,0,0,0,66,40.11L63.5,62.39,62.39,63.5,40.1,66A12,12,0,0,0,31,71.89,111.67,111.67,0,0,0,19.77,99.12,12,12,0,0,0,22,109.7l14,17.51v1.58L22,146.3a12,12,0,0,0-2.23,10.59,111.75,111.75,0,0,0,11.29,27.22A12,12,0,0,0,40.11,190l22.28,2.48,1.11,1.11L66,215.9A12,12,0,0,0,71.89,225a111.67,111.67,0,0,0,27.23,11.27A12,12,0,0,0,109.7,234l17.51-14h1.58l17.51,14a12,12,0,0,0,10.59,2.23A111.75,111.75,0,0,0,184.11,225a12,12,0,0,0,5.91-9.06l2.48-22.28,1.11-1.11L215.9,190a12,12,0,0,0,9.06-5.91,111.67,111.67,0,0,0,11.27-27.23A12,12,0,0,0,234,146.3Zm-24.12-4.89a70.1,70.1,0,0,1,0,8.2,12,12,0,0,0,2.61,8.22l12.84,16.05A86.47,86.47,0,0,1,207,166.86l-20.43,2.27a12,12,0,0,0-7.65,4,69,69,0,0,1-5.8,5.8,12,12,0,0,0-4,7.65L166.86,207a86.47,86.47,0,0,1-10.49,4.35l-16.05-12.85a12,12,0,0,0-7.5-2.62c-.24,0-.48,0-.72,0a70.1,70.1,0,0,1-8.2,0,12.06,12.06,0,0,0-8.22,2.6L99.63,211.33A86.47,86.47,0,0,1,89.14,207l-2.27-20.43a12,12,0,0,0-4-7.65,69,69,0,0,1-5.8-5.8,12,12,0,0,0-7.65-4L49,166.86a86.47,86.47,0,0,1-4.35-10.49l12.84-16.05a12,12,0,0,0,2.61-8.22,70.1,70.1,0,0,1,0-8.2,12,12,0,0,0-2.61-8.22L44.67,99.63A86.47,86.47,0,0,1,49,89.14l20.43-2.27a12,12,0,0,0,7.65-4,69,69,0,0,1,5.8-5.8,12,12,0,0,0,4-7.65L89.14,49a86.47,86.47,0,0,1,10.49-4.35l16.05,12.85a12.06,12.06,0,0,0,8.22,2.6,70.1,70.1,0,0,1,8.2,0,12,12,0,0,0,8.22-2.6l16.05-12.85A86.47,86.47,0,0,1,166.86,49l2.27,20.43a12,12,0,0,0,4,7.65,69,69,0,0,1,5.8,5.8,12,12,0,0,0,7.65,4L207,89.14a86.47,86.47,0,0,1,4.35,10.49l-12.84,16.05A12,12,0,0,0,195.88,123.9Z"
        readonly property string collapse: "M168.49,199.51a12,12,0,0,1-17,17l-80-80a12,12,0,0,1,0-17l80-80a12,12,0,0,1,17,17L97,128Z"
        readonly property string folder: "M216,68H133.39l-26-29.29a20,20,0,0,0-15-6.71H40A20,20,0,0,0,20,52V200.62A19.41,19.41,0,0,0,39.38,220H216.89A19.13,19.13,0,0,0,236,200.89V88A20,20,0,0,0,216,68ZM44,56H90.61l10.67,12H44ZM212,196H44V92H212Z"
        readonly property string wrench: "M230.47,67.5a12,12,0,0,0-19.26-4.32L172.43,99l-12.68-2.72L157,83.57l35.79-38.78a12,12,0,0,0-4.32-19.26A76.07,76.07,0,0,0,88.41,121.64L30.92,174.18a4.68,4.68,0,0,0-.39.38,36,36,0,0,0,50.91,50.91l.38-.39,52.54-57.49A76.05,76.05,0,0,0,230.47,67.5ZM160,148a51.5,51.5,0,0,1-23.35-5.52,12,12,0,0,0-14.26,2.62L64.31,208.66a12,12,0,0,1-17-17l63.55-58.07a12,12,0,0,0,2.62-14.26A51.5,51.5,0,0,1,108,96a52.06,52.06,0,0,1,52-52h.89L135.17,71.87a12,12,0,0,0-2.91,10.65l5.66,26.35a12,12,0,0,0,9.21,9.21l26.35,5.66a12,12,0,0,0,10.65-2.91L212,95.12c0,.3,0,.59,0,.89A52.06,52.06,0,0,1,160,148Z"
        readonly property string edit: "M230.14,70.54,185.46,25.85a20,20,0,0,0-28.29,0L33.86,149.17A19.85,19.85,0,0,0,28,163.31V208a20,20,0,0,0,20,20H92.69a19.86,19.86,0,0,0,14.14-5.86L230.14,98.82a20,20,0,0,0,0-28.28ZM91,204H52V165l84-84,39,39ZM192,103,153,64l18.34-18.34,39,39Z"
        readonly property string refresh: "M228,48V96a12,12,0,0,1-12,12H168a12,12,0,0,1,0-24h19l-7.8-7.8a75.55,75.55,0,0,0-53.32-22.26h-.43A75.49,75.49,0,0,0,72.39,75.57,12,12,0,1,1,55.61,58.41a99.38,99.38,0,0,1,69.87-28.47H126A99.42,99.42,0,0,1,196.2,59.23L204,67V48a12,12,0,0,1,24,0ZM183.61,180.43a75.49,75.49,0,0,1-53.09,21.63h-.43A75.55,75.55,0,0,1,76.77,179.8L69,172H88a12,12,0,0,0,0-24H40a12,12,0,0,0-12,12v48a12,12,0,0,0,24,0V189l7.8,7.8A99.42,99.42,0,0,0,130,226.06h.56a99.38,99.38,0,0,0,69.87-28.47,12,12,0,0,0-16.78-17.16Z"
        readonly property string plus: "M228,128a12,12,0,0,1-12,12H140v76a12,12,0,0,1-24,0V140H40a12,12,0,0,1,0-24h76V40a12,12,0,0,1,24,0v76h76A12,12,0,0,1,228,128Z"
        readonly property string updown: "M120.49,167.51a12,12,0,0,1,0,17l-32,32a12,12,0,0,1-17,0l-32-32a12,12,0,1,1,17-17L68,179V48a12,12,0,0,1,24,0V179l11.51-11.52A12,12,0,0,1,120.49,167.51Zm96-96-32-32a12,12,0,0,0-17,0l-32,32a12,12,0,0,0,17,17L164,77V208a12,12,0,0,0,24,0V77l11.51,11.52a12,12,0,0,0,17-17Z"
        readonly property string arrowUp: "M208.49,120.49a12,12,0,0,1-17,0L140,69V216a12,12,0,0,1-24,0V69L64.49,120.49a12,12,0,0,1-17-17l72-72a12,12,0,0,1,17,0l72,72A12,12,0,0,1,208.49,120.49Z"
        readonly property string check: "M232.49,80.49l-128,128a12,12,0,0,1-17,0l-56-56a12,12,0,1,1,17-17L96,183,215.51,63.51a12,12,0,0,1,17,17Z"
        readonly property string power: "M116,128V48a12,12,0,0,1,24,0v80a12,12,0,0,1-24,0Zm66.55-82a12,12,0,0,0-13.1,20.1C191.41,80.37,204,103,204,128a76,76,0,0,1-152,0c0-25,12.59-47.63,34.55-61.95A12,12,0,0,0,73.45,46C44.56,64.78,28,94.69,28,128a100,100,0,0,0,200,0C228,94.69,211.44,64.78,182.55,46Z"
        readonly property string trash: "M216,48H180V36A28,28,0,0,0,152,8H104A28,28,0,0,0,76,36V48H40a12,12,0,0,0,0,24h4V208a20,20,0,0,0,20,20H192a20,20,0,0,0,20-20V72h4a12,12,0,0,0,0-24ZM100,36a4,4,0,0,1,4-4h48a4,4,0,0,1,4,4V48H100Zm88,168H68V72H188ZM116,104v64a12,12,0,0,1-24,0V104a12,12,0,0,1,24,0Zm48,0v64a12,12,0,0,1-24,0V104a12,12,0,0,1,24,0Z"
        readonly property string search: "M232.49,215.51,185,168a92.12,92.12,0,1,0-17,17l47.53,47.54a12,12,0,0,0,17-17ZM44,112a68,68,0,1,1,68,68A68.07,68.07,0,0,1,44,112Z"
        readonly property string profiles: "M100,36H56A20,20,0,0,0,36,56v44a20,20,0,0,0,20,20h44a20,20,0,0,0,20-20V56A20,20,0,0,0,100,36ZM96,96H60V60H96ZM200,36H156a20,20,0,0,0-20,20v44a20,20,0,0,0,20,20h44a20,20,0,0,0,20-20V56A20,20,0,0,0,200,36Zm-4,60H160V60h36Zm-96,40H56a20,20,0,0,0-20,20v44a20,20,0,0,0,20,20h44a20,20,0,0,0,20-20V156A20,20,0,0,0,100,136Zm-4,60H60V160H96Zm104-60H156a20,20,0,0,0-20,20v44a20,20,0,0,0,20,20h44a20,20,0,0,0,20-20V156A20,20,0,0,0,200,136Zm-4,60H160V160h36Z"
        readonly property string rename: "M246.15,133.18,146.83,33.86A19.85,19.85,0,0,0,132.69,28H40A12,12,0,0,0,28,40v92.69a19.85,19.85,0,0,0,5.86,14.14l99.32,99.32a20,20,0,0,0,28.28,0l84.69-84.69A20,20,0,0,0,246.15,133.18Zm-98.83,93.17L52,131V52h79l95.32,95.32ZM104,88A16,16,0,1,1,88,72,16,16,0,0,1,104,88Z"
    }


    function acc(a) { return Qt.rgba(th.accent.r, th.accent.g, th.accent.b, a) }
    function rgba(c, a) { return Qt.rgba(c.r, c.g, c.b, a) }
    function ui(key) { return backend.uiRevision, backend.tr(key) }
    function statusDot(s) {
        return s === "active" ? th.stActiveDot : s === "disabled" ? th.stDisabledDot
             : s === "notinlist" ? th.stNotinDot : s === "duplicate" ? th.stDupDot : th.dim
    }
    function statusTextColor(s) {
        return s === "active" ? th.stActiveText : s === "disabled" ? th.stDisabledText
             : s === "notinlist" ? th.stNotinText : s === "duplicate" ? th.stDupText : th.dim
    }
    function statusLabel(s) {
        return s === "active" ? root.ui("manage_state_active")
             : s === "disabled" ? root.ui("manage_state_disabled")
             : s === "notinlist" ? root.ui("manage_state_unlisted")
             : root.ui("manage_state_duplicate")
    }
    function tagColor(g) {
        return g === "DLC" ? th.accent : g === "ELS" ? th.tagEls : g === "XML" ? th.tagXml : th.tagInfo
    }
    function glyphChar(st) { return st === "ok" ? "✓" : st === "err" ? "✗" : st === "work" ? "→" : "•" }
    function glyphColor(st) { return st === "ok" ? th.glyphOk : st === "err" ? th.glyphErr : th.glyphRun }









    component AvIcon: Item {
        id: ic
        property string path: ""
        property real size: 18
        property real sw: 1.6
        property color color: "#ffffff"
        property real box: 256
        property bool filled: true
        implicitWidth: size; implicitHeight: size
        width: size; height: size
        Shape {
            anchors.fill: parent
            antialiasing: true
            preferredRendererType: Shape.GeometryRenderer
            ShapePath {
                strokeColor: ic.filled ? "transparent" : ic.color
                strokeWidth: ic.sw
                fillColor: ic.filled ? ic.color : "transparent"
                fillRule: ShapePath.WindingFill
                capStyle: ShapePath.RoundCap
                joinStyle: ShapePath.RoundJoin
                PathSvg { path: ic.path }
            }
            transform: Scale { xScale: ic.size / ic.box; yScale: ic.size / ic.box }
        }
    }



    component DashedBox: Canvas {
        id: dbx
        property color stroke: th.dropDash
        property real rad: th.rLg
        onStrokeChanged: requestPaint()
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        Component.onCompleted: requestPaint()
        onPaint: {
            var ctx = getContext("2d")
            ctx.reset()
            var w = width, h = height, r = dbx.rad, off = 1
            ctx.lineWidth = 1.5
            ctx.strokeStyle = dbx.stroke
            ctx.setLineDash([6, 5])
            ctx.beginPath()
            ctx.moveTo(off + r, off)
            ctx.lineTo(w - off - r, off); ctx.arcTo(w - off, off, w - off, off + r, r)
            ctx.lineTo(w - off, h - off - r); ctx.arcTo(w - off, h - off, w - off - r, h - off, r)
            ctx.lineTo(off + r, h - off); ctx.arcTo(off, h - off, off, h - off - r, r)
            ctx.lineTo(off, off + r); ctx.arcTo(off, off, off + r, off, r)
            ctx.closePath()
            ctx.stroke()
        }
    }


    component StatusDot: Item {
        id: sd
        property string status: "active"
        property real size: 8
        property bool ring: false
        property color dotColor: root.statusDot(status)
        implicitWidth: size; implicitHeight: size
        Rectangle {
            visible: sd.ring
            anchors.centerIn: parent
            width: sd.size + 6; height: sd.size + 6; radius: width / 2
            color: root.rgba(sd.dotColor, 0.22)
        }
        Rectangle {
            anchors.centerIn: parent
            width: sd.size; height: sd.size; radius: width / 2
            color: sd.dotColor
        }
    }


    component AvToggle: Item {
        id: tg
        property bool on: false
        signal toggled()
        implicitWidth: 38; implicitHeight: 22
        Rectangle {
            anchors.fill: parent
            radius: 4
            color: tg.on ? th.accent : th.knobOff
            Behavior on color { ColorAnimation { duration: 180 } }
            Rectangle {
                y: 2; width: 18; height: 18; radius: 3; color: "#ffffff"
                x: tg.on ? parent.width - width - 2 : 2
                Behavior on x { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }
            }
        }
        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: tg.toggled() }
    }


    component AvCheck: Item {
        id: ck
        property bool on: false
        property real size: 17
        signal toggled()
        implicitWidth: size; implicitHeight: size
        Rectangle {
            anchors.fill: parent
            radius: 4
            color: ck.on ? th.accent : "transparent"
            border.width: ck.on ? 0 : 1.5
            border.color: th.checkBorder
            AvIcon {
                anchors.centerIn: parent
                visible: ck.on
                path: ico.check; size: ck.size - 5; sw: 2.4; color: "#ffffff"
            }
        }
        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: ck.toggled() }
    }


    component AvPill: Rectangle {
        id: pl
        property string status: "active"
        implicitHeight: 22
        implicitWidth: lbl.implicitWidth + 18
        radius: 4
        color: root.rgba(root.statusDot(status), 0.14)
        border.width: 1
        border.color: root.rgba(root.statusDot(status), 0.30)
        Text {
            id: lbl
            anchors.centerIn: parent
            text: root.statusLabel(pl.status)
            color: root.statusTextColor(pl.status)
            font.family: th.ui; font.pixelSize: 11; font.weight: Font.DemiBold
        }
    }


    component AvButton: Item {
        id: bt
        property string kind: "ghost"
        property string text: ""
        property string iconPath: ""
        property string size: "md"            
        signal clicked()

        readonly property int h: size === "sm" ? 32 : size === "lg" ? 44 : 38
        readonly property int padH: size === "sm" ? 14 : 18
        readonly property color baseBg:
            kind === "solid" ? th.accent :
            kind === "soft"  ? root.acc(0.16) :
            kind === "danger" ? "transparent" : th.ghostBg
        readonly property color contentColor:
            kind === "solid" ? "#ffffff" :
            kind === "soft"  ? th.accentText :
            kind === "danger" ? th.dangerText : th.ghostText
        readonly property color borderColor:
            kind === "solid" ? "transparent" :
            kind === "soft"  ? root.acc(0.24) :
            kind === "danger" ? root.rgba(th.stDupDot, 0.34) : th.ghostBorder

        implicitHeight: h
        implicitWidth: rowc.implicitWidth + padH * 2
        opacity: enabled ? 1 : 0.4

        scale: ma.pressed ? 0.95 : 1.0
        Behavior on scale { NumberAnimation { duration: 90; easing.type: Easing.OutCubic } }

        Rectangle {
            id: bg
            anchors.fill: parent
            radius: th.rBtn
            border.width: 1
            border.color: bt.borderColor
            color: {
                if (ma.pressed) {
                    if (bt.kind === "solid") return Qt.darker(th.accent, 1.25)
                    if (bt.kind === "soft") return root.acc(0.34)
                    if (bt.kind === "danger") return root.rgba(th.stDupDot, 0.22)
                    return Qt.lighter(th.ghostBg, 2.0)
                }
                if (!ma.containsMouse) return bt.baseBg
                if (bt.kind === "solid") return Qt.lighter(th.accent, 1.10)
                if (bt.kind === "soft") return root.acc(0.24)
                if (bt.kind === "danger") return root.rgba(th.stDupDot, 0.12)
                return Qt.lighter(th.ghostBg, 1.5)
            }
            Behavior on color { ColorAnimation { duration: 120 } }
        }
        RowLayout {
            id: rowc
            anchors.centerIn: parent
            spacing: 8
            AvIcon {
                visible: bt.iconPath.length > 0
                path: bt.iconPath
                size: bt.size === "sm" ? 15 : 16
                color: bt.contentColor
            }
            Text {
                visible: bt.text.length > 0
                text: bt.text
                color: bt.contentColor
                font.family: th.ui
                font.pixelSize: bt.size === "sm" ? 12.5 : 13.5
                font.weight: Font.DemiBold
            }
        }
        MouseArea {
            id: ma
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            enabled: bt.enabled
            onClicked: bt.clicked()
        }
    }


    component Eyebrow: Text {
        font.family: th.ui
        font.pixelSize: 12
        font.weight: Font.DemiBold
        color: th.dim
        leftPadding: 6
    }


    component PageHeader: ColumnLayout {
        property string title: ""
        property string subtitle: ""
        spacing: 6
        Text {
            text: parent.title
            color: th.textHi
            font.family: th.disp; font.pixelSize: 23; font.weight: Font.DemiBold
        }
        Text {
            visible: parent.subtitle.length > 0
            text: parent.subtitle
            color: th.mute
            font.family: th.ui; font.pixelSize: 13
            textFormat: Text.StyledText
        }
    }




    Rectangle {
        id: container
        anchors.fill: parent
        radius: root.maximized ? 0 : 10
        color: th.appBg
        border.color: th.cardBorder
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            spacing: 0


            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: 46

                MouseArea {
                    anchors.fill: parent
                    onPressed: root.startSystemMove()
                    onDoubleClicked: root.maximized ? root.showNormal() : root.showMaximized()
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 18
                    anchors.rightMargin: 8
                    spacing: 0

                    Image {
                        source: "../logo-trim.png"
                        sourceSize.height: 24
                        fillMode: Image.PreserveAspectFit
                        Layout.preferredHeight: 24
                    }
                    Text {
                        text: "v" + backend.version
                        color: th.faint
                        font.family: th.mono; font.pixelSize: 11
                        Layout.leftMargin: 11
                    }

                    Item { Layout.fillWidth: true }


                    Rectangle {
                        id: safeBox
                        Layout.preferredHeight: 28
                        Layout.preferredWidth: connRow.implicitWidth + 24
                        radius: th.rBtn
                        color: safeMa.containsMouse ? Qt.lighter(th.card, 1.5) : th.card
                        border.color: th.cardBorder
                        Behavior on color { ColorAnimation { duration: 120 } }
                        RowLayout {
                            id: connRow
                            anchors.centerIn: parent
                            spacing: 8
                            StatusDot { status: backend.useModsFolder ? "active" : "duplicate"; ring: true }
                            Text {
                                text: backend.useModsFolder ? root.ui("safebox_title") : root.ui("unsafe_title")
                                color: th.dim
                                font.family: th.ui; font.pixelSize: 11; font.weight: Font.DemiBold
                            }
                        }
                        MouseArea {
                            id: safeMa
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: backend.setUseModsFolder(!backend.useModsFolder)
                            ToolTip.visible: containsMouse
                            ToolTip.text: backend.useModsFolder ? root.ui("beh_safe_desc") : root.ui("safebox_desc")
                        }
                    }


                    RowLayout {
                        Layout.leftMargin: 14
                        Layout.fillHeight: true
                        spacing: 0
                        Repeater {
                            model: ["min", "max", "close"]
                            delegate: Rectangle {
                                required property int index
                                required property string modelData
                                Layout.fillHeight: true
                                Layout.preferredWidth: 46
                                radius: 0
                                color: wma.containsMouse
                                       ? (modelData === "close" ? th.closeHover : root.rgba(Qt.rgba(1,1,1,1), 0.07))
                                       : "transparent"
                                Behavior on color { ColorAnimation { duration: 110 } }
                                AvIcon {
                                    anchors.centerIn: parent
                                    filled: false
                                    box: 12; size: 12; sw: 1.2
                                    color: (modelData === "close" && wma.containsMouse) ? "#ffffff"
                                           : modelData === "close" ? "#c9ccd2" : th.mute
                                    path: modelData === "min" ? "M2.5 6h7"
                                          : modelData === "max" ? "M3.2 3.2h5.6v5.6h-5.6z"
                                          : "M3 3l6 6 M9 3l-6 6"
                                }
                                MouseArea {
                                    id: wma
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: {
                                        if (modelData === "min") root.showMinimized()
                                        else if (modelData === "max") root.maximized ? root.showNormal() : root.showMaximized()
                                        else root.close()
                                    }
                                }
                            }
                        }
                    }
                }
            }


            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.topMargin: 2
                Layout.leftMargin: 14
                Layout.rightMargin: 14
                Layout.bottomMargin: 14
                spacing: 14


                Rectangle {
                    id: sidebar
                    objectName: "sidebar"
                    Layout.fillHeight: true
                    Layout.preferredWidth: collapsed ? 70 : 224
                    radius: th.rLg
                    color: th.card
                    border.color: th.cardBorder


                    readonly property bool collapsed: backend.sidebarAutoCollapse
                                                      ? !sidebarHover.hovered
                                                      : backend.sidebarCollapsed
                    HoverHandler { id: sidebarHover }
                    Behavior on Layout.preferredWidth {
                        NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
                    }

                    ColumnLayout {


                        anchors.fill: parent
                        anchors.topMargin: 14
                        anchors.bottomMargin: 14
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        spacing: 5


                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 34
                            Layout.bottomMargin: 3
                            radius: th.rSm
                            color: collMa.containsMouse ? Qt.lighter(th.card, 1.5) : "transparent"
                            Text {
                                anchors.left: parent.left
                                anchors.leftMargin: 12
                                anchors.verticalCenter: parent.verticalCenter
                                text: root.ui("nav_menu")
                                color: th.mute
                                font.family: th.ui; font.pixelSize: 11; font.weight: Font.DemiBold
                                opacity: sidebar.collapsed ? 0 : 1
                                Behavior on opacity { NumberAnimation { duration: 150 } }
                                visible: opacity > 0.01
                            }
                            AvIcon {



                                anchors.right: parent.right
                                anchors.rightMargin: 14
                                anchors.verticalCenter: parent.verticalCenter
                                path: ico.collapse; size: 18; color: th.mute
                                rotation: sidebar.collapsed ? 0 : 180
                                Behavior on rotation { NumberAnimation { duration: 200 } }
                            }
                            MouseArea {
                                id: collMa
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                enabled: !backend.sidebarAutoCollapse
                                onClicked: backend.setSidebarCollapsed(!backend.sidebarCollapsed)
                            }
                        }


                        Repeater {
                            model: [
                                { icon: ico.install,  key: "tab_install" },
                                { icon: ico.packs,    key: "tab_mods" },
                                { icon: ico.folder,   key: "tab_els" },
                                { icon: ico.profiles, key: "tab_profiles" },
                                { icon: ico.rename,   key: "tab_rename" },
                                { icon: ico.settings, key: "tab_settings" }
                            ]
                            delegate: Rectangle {
                                required property int index
                                required property var modelData
                                Layout.fillWidth: true
                                Layout.preferredHeight: 42
                                radius: th.rSm
                                property bool active: root.currentPage === index
                                color: active ? root.acc(0.16)
                                       : navMa.containsMouse ? Qt.lighter(th.card, 1.5) : "transparent"
                                Behavior on color { ColorAnimation { duration: 130 } }



                                AvIcon {
                                    id: navIcon
                                    anchors.left: parent.left
                                    anchors.leftMargin: 14
                                    anchors.verticalCenter: parent.verticalCenter
                                    path: modelData.icon
                                    size: 18
                                    sw: active ? 1.9 : 1.6
                                    color: active ? "#ffffff" : th.dim
                                }
                                Text {
                                    anchors.left: navIcon.right
                                    anchors.leftMargin: 12
                                    anchors.right: parent.right
                                    anchors.rightMargin: 10
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: root.ui(modelData.key)
                                    color: active ? "#ffffff" : th.dim
                                    font.family: th.ui; font.pixelSize: 13
                                    font.weight: active ? Font.DemiBold : Font.Medium
                                    elide: Text.ElideRight
                                    opacity: sidebar.collapsed ? 0 : 1
                                    Behavior on opacity { NumberAnimation { duration: 150 } }
                                    visible: opacity > 0.01
                                }
                                MouseArea {
                                    id: navMa
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: root.currentPage = index
                                    ToolTip.visible: sidebar.collapsed && containsMouse
                                    ToolTip.text: root.ui(modelData.key)
                                }
                            }
                        }

                        Item { Layout.fillHeight: true }
                    }
                }


                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    Repeater {
                        model: 6
                        delegate: Item {
                            required property int index
                            anchors.fill: parent
                            visible: opacity > 0.01
                            opacity: root.currentPage === index ? 1 : 0
                            Behavior on opacity { NumberAnimation { duration: 150 } }
                            transform: Translate {
                                x: root.currentPage === index ? 0 : 14
                                Behavior on x { NumberAnimation { duration: 150; easing.type: Easing.OutCubic } }
                            }
                            Loader {
                                anchors.fill: parent
                                active: true
                                sourceComponent: index === 0 ? installPage
                                                 : index === 1 ? packsPage
                                                 : index === 2 ? elsPage
                                                 : index === 3 ? profilesPage
                                                 : index === 4 ? renamePage : settingsPage
                            }
                        }
                    }
                }
            }
        }


        MouseArea {
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            width: 18; height: 18
            cursorShape: Qt.SizeFDiagCursor
            onPressed: root.startSystemResize(Qt.RightEdge | Qt.BottomEdge)
        }
    }




    Component {
        id: installPage
        ColumnLayout {
            spacing: 16

            PageHeader {
                Layout.fillWidth: true
                title: root.ui("tab_install")
                subtitle: root.ui("subtitle_placeholder")
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 16


                ColumnLayout {
                    Layout.preferredWidth: 56
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 16


                    Item {
                        id: zonesGrid
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        readonly property int gap: 12
                        readonly property real cellW: (width  - gap) / 2
                        readonly property real cellH: (height - gap) / 2

                        function cellX(c) { return c * (cellW + gap) }
                        function cellY(r) { return r * (cellH + gap) }
                        function spanW(w) { return w * cellW + (w - 1) * gap }
                        function spanH(h) { return h * cellH + (h - 1) * gap }


                        function cellCovered(c, r) {
                            var z = backend.dropZones
                            for (var i = 0; i < z.length; i++) {
                                var zz = z[i]
                                if (c >= zz.col && c < zz.col + zz.w &&
                                    r >= zz.row && r < zz.row + zz.h) return true
                            }
                            return false
                        }

                        function freeCells() {
                            var out = []
                            for (var r = 0; r < 2; r++)
                                for (var c = 0; c < 2; c++)
                                    if (!cellCovered(c, r)) out.push({ c: c, r: r })
                            return out
                        }
                        property var free: freeCells()


                        Repeater {
                            model: backend.dropZones
                            delegate: Item {
                                id: zoneItem
                                required property var modelData
                                property bool over: zda.containsDrag || zhover.containsMouse

                                x: zonesGrid.cellX(modelData.col)
                                y: zonesGrid.cellY(modelData.row)
                                width:  zonesGrid.spanW(modelData.w)
                                height: zonesGrid.spanH(modelData.h)

                                Rectangle { anchors.fill: parent; radius: th.rLg; color: th.dropBg }
                                Rectangle {
                                    anchors.fill: parent; radius: th.rLg
                                    visible: zoneItem.over; color: root.acc(0.08)
                                }
                                DashedBox {
                                    anchors.fill: parent
                                    stroke: zoneItem.over ? th.accent : th.dropDash
                                }


                                ColumnLayout {
                                    anchors.centerIn: parent
                                    width: parent.width - 32
                                    spacing: zoneItem.height < 160 ? 8 : 16
                                    Rectangle {
                                        Layout.alignment: Qt.AlignHCenter
                                        width: 64; height: 64; radius: th.rIcon
                                        color: root.acc(0.15)
                                        y: zoneItem.over ? -3 : 0
                                        scale: zoneItem.over ? 1.04 : 1.0
                                        Behavior on y { NumberAnimation { duration: 200 } }
                                        Behavior on scale { NumberAnimation { duration: 200 } }
                                        AvIcon {
                                            anchors.centerIn: parent
                                            path: modelData.auto ? ico.install : ico.folder
                                            size: 28; color: th.accent
                                        }
                                    }
                                    Text {
                                        Layout.alignment: Qt.AlignHCenter
                                        Layout.fillWidth: true
                                        horizontalAlignment: Text.AlignHCenter
                                        text: modelData.name
                                        color: th.textHi
                                        font.family: th.disp; font.pixelSize: 18; font.weight: Font.DemiBold
                                        elide: Text.ElideRight
                                    }
                                    Text {
                                        Layout.alignment: Qt.AlignHCenter
                                        Layout.fillWidth: true
                                        horizontalAlignment: Text.AlignHCenter
                                        text: modelData.auto ? root.ui("zone_auto_desc")
                                              : (modelData.rel.length > 0 ? modelData.rel : root.ui("zone_target_root"))
                                        color: th.mute
                                        font.family: modelData.auto ? th.ui : th.mono
                                        font.pixelSize: 12
                                        elide: Text.ElideMiddle
                                        maximumLineCount: 2
                                        wrapMode: Text.WrapAnywhere
                                    }
                                    AvButton {
                                        Layout.alignment: Qt.AlignHCenter
                                        visible: modelData.auto
                                        kind: "solid"; iconPath: ico.folder; size: "sm"
                                        text: root.ui("choose_files_btn")
                                        onClicked: backend.chooseArchives()
                                    }
                                    Text {
                                        Layout.alignment: Qt.AlignHCenter
                                        visible: !modelData.auto
                                        text: root.ui("zone_drop_hint")
                                        color: th.accent
                                        font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                                    }
                                }


                                RowLayout {
                                    anchors.top: parent.top
                                    anchors.right: parent.right
                                    anchors.topMargin: 10
                                    anchors.rightMargin: 10
                                    spacing: 6
                                    opacity: zoneItem.over ? 1 : 0
                                    visible: opacity > 0.01
                                    Behavior on opacity { NumberAnimation { duration: 140 } }
                                    Repeater {
                                        model: [
                                            { ic: ico.edit,   act: "edit" },
                                            { ic: ico.folder, act: "open" },
                                            { ic: ico.trash,  act: "remove" }
                                        ]
                                        delegate: Rectangle {
                                            required property var modelData
                                            width: 28; height: 28; radius: th.rSm
                                            color: tbm.containsMouse ? Qt.lighter(th.card, 1.6) : th.card
                                            border.color: th.cardBorder
                                            AvIcon {
                                                anchors.centerIn: parent
                                                path: modelData.ic; size: 15
                                                color: modelData.act === "remove" ? th.dangerText : th.dim
                                            }
                                            MouseArea {
                                                id: tbm
                                                anchors.fill: parent; hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: {
                                                    if (modelData.act === "edit") zoneEditor.openEdit(zoneItem.modelData)
                                                    else if (modelData.act === "open") backend.openZoneFolder(zoneItem.modelData.id)
                                                    else backend.removeZone(zoneItem.modelData.id)
                                                }
                                            }
                                        }
                                    }
                                }

                                MouseArea {
                                    id: zhover
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    acceptedButtons: Qt.NoButton
                                }
                                DropArea {
                                    id: zda
                                    anchors.fill: parent
                                    onDropped: function(drop) {
                                        if (drop.hasUrls) backend.dropToZone(zoneItem.modelData.id, drop.urls)
                                    }
                                }
                            }
                        }


                        Repeater {
                            model: zonesGrid.free
                            delegate: Item {
                                id: addCell
                                required property var modelData
                                property bool hov: addMa.containsMouse
                                x: zonesGrid.cellX(modelData.c)
                                y: zonesGrid.cellY(modelData.r)
                                width: zonesGrid.cellW
                                height: zonesGrid.cellH

                                Rectangle {
                                    anchors.fill: parent; radius: th.rLg
                                    color: addCell.hov ? root.acc(0.06) : "transparent"
                                }
                                DashedBox {
                                    anchors.fill: parent
                                    stroke: addCell.hov ? th.accent : th.innerBorder
                                }
                                ColumnLayout {
                                    anchors.centerIn: parent
                                    spacing: 9
                                    Rectangle {
                                        Layout.alignment: Qt.AlignHCenter
                                        width: 46; height: 46; radius: th.rIcon
                                        color: addCell.hov ? root.acc(0.15) : th.innerBox
                                        AvIcon {
                                            anchors.centerIn: parent; path: ico.plus; size: 22
                                            color: addCell.hov ? th.accent : th.mute
                                        }
                                    }
                                    Text {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: root.ui("zones_add")
                                        color: addCell.hov ? th.dim : th.mute
                                        font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                                    }
                                }
                                MouseArea {
                                    id: addMa
                                    anchors.fill: parent; hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: zoneEditor.openNew(modelData.c, modelData.r)
                                }
                            }
                        }
                    }



                    RowLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: false
                        Layout.preferredHeight: 80
                        spacing: 16
                        Repeater {
                            model: [
                                { value: backend.packsActive, label: root.ui("metric_packs_active"), st: "active" },
                                { value: backend.elsSets,     label: root.ui("metric_els_sets"),     st: "active" },
                                { value: backend.hintsCount,  label: root.ui("metric_hints"),        st: "notinlist" }
                            ]
                            delegate: Rectangle {
                                required property var modelData
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                radius: th.rMd
                                color: th.card
                                border.color: th.cardBorder
                                ColumnLayout {
                                    anchors.verticalCenter: parent.verticalCenter
                                    anchors.left: parent.left
                                    anchors.leftMargin: 18
                                    spacing: 4
                                    RowLayout {
                                        spacing: 9
                                        StatusDot { status: modelData.st }
                                        Text {
                                            text: modelData.value
                                            color: th.textHi
                                            font.family: th.disp; font.pixelSize: 24; font.weight: Font.DemiBold
                                        }
                                    }
                                    Text {
                                        text: modelData.label
                                        color: th.mute
                                        font.family: th.ui; font.pixelSize: 11
                                    }
                                }
                            }
                        }
                    }
                }


                ColumnLayout {
                    Layout.preferredWidth: 44
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 16


                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: th.rLg
                        color: th.card
                        border.color: th.cardBorder
                        clip: true

                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 0


                            Item {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 42
                                Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: th.divider }
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 16
                                    anchors.rightMargin: 16
                                    Text {
                                        text: root.ui("install_log_title")
                                        color: th.dim
                                        font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                                    }
                                    Item { Layout.fillWidth: true }
                                    Text {
                                        text: root.ui("log_autoscroll")
                                        color: th.faint
                                        font.family: th.mono; font.pixelSize: 11
                                    }
                                }
                            }


                            ListView {
                                id: logView
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Layout.margins: 12
                                Layout.leftMargin: 16
                                Layout.rightMargin: 16
                                clip: true
                                model: ListModel { id: logModel }
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                                delegate: RowLayout {
                                    required property int index
                                    required property string group
                                    required property string status
                                    required property string lineText
                                    width: logView.width
                                    spacing: 10
                                    Text {
                                        text: index + 1
                                        color: th.lineNum
                                        font.family: th.mono; font.pixelSize: 12
                                        horizontalAlignment: Text.AlignRight
                                        Layout.preferredWidth: 22
                                        Layout.alignment: Qt.AlignTop
                                    }
                                    Text {
                                        text: root.glyphChar(status)
                                        color: root.glyphColor(status)
                                        font.family: th.mono; font.pixelSize: 12; font.weight: Font.Bold
                                        Layout.preferredWidth: 12
                                        Layout.alignment: Qt.AlignTop
                                    }
                                    Text {
                                        text: "[" + group + "]"
                                        color: root.tagColor(group)
                                        font.family: th.mono; font.pixelSize: 12; font.weight: Font.DemiBold
                                        Layout.preferredWidth: 38
                                        Layout.alignment: Qt.AlignTop
                                    }
                                    Text {
                                        text: lineText
                                        color: "#b6bcc4"
                                        font.family: th.mono; font.pixelSize: 12
                                        lineHeight: 1.4
                                        wrapMode: Text.Wrap
                                        Layout.fillWidth: true
                                    }
                                }
                            }


                            Rectangle {
                                Layout.fillWidth: true
                                Layout.leftMargin: 16
                                Layout.rightMargin: 16
                                Layout.bottomMargin: 12
                                Layout.preferredHeight: 4
                                radius: 2
                                visible: progressBar.frac >= 0
                                color: th.innerBox
                                Rectangle {
                                    id: progressBar
                                    property real frac: -1
                                    width: parent.width * Math.max(0, frac)
                                    height: parent.height; radius: 2; color: th.accent
                                }
                            }


                        }
                    }


                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 80
                        radius: th.rMd
                        color: th.card
                        border.color: th.cardBorder
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 18
                            anchors.rightMargin: 18
                            spacing: 14
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2
                                Text {
                                    text: root.ui("gta_eyebrow")
                                    color: th.dim
                                    font.family: th.ui; font.pixelSize: 11; font.weight: Font.DemiBold
                                }
                                Text {
                                    Layout.fillWidth: true
                                    text: backend.gtaPath.length > 0 ? backend.gtaPath : root.ui("path_unset_short")
                                    color: th.dim
                                    font.family: th.mono; font.pixelSize: 12
                                    elide: Text.ElideMiddle
                                }
                            }
                            AvButton {
                                kind: "ghost"; size: "sm"; iconPath: ico.wrench
                                text: root.ui("change_btn")
                                onClicked: backend.chooseGtaPath()
                            }
                        }
                    }
                }
            }


            Component.onCompleted: {
                var h = backend.history
                for (var i = 0; i < h.length; i++)
                    logModel.append({ group: h[i].group, status: h[i].status, lineText: h[i].text })
                logView.positionViewAtEnd()
            }
            Connections {
                target: backend
                function onLogAppended(group, status, text) {
                    logModel.append({ group: group, status: status, lineText: text })
                    logView.positionViewAtEnd()
                }
                function onProgress(frac, label) { progressBar.frac = frac }
            }
        }
    }




    Component {
        id: packsPage
        ColumnLayout {
            id: packsRoot
            objectName: "packsRoot"
            spacing: 16



            property string sortKey: backend.packSortKey === "created" ? "added" : backend.packSortKey
            property string sortDir: backend.packSortDir
            property string search: ""
            property var selMap: ({})
            property int selVer: 0

            readonly property var sortDefs: [
                { key: "name",   label: root.ui("sort_name") },
                { key: "added",  label: root.ui("sort_added") },
                { key: "status", label: root.ui("col_status") }
            ]




            ListModel { id: packsModel }


            function statusRank(s) {
                return s === "active" ? 0 : s === "disabled" ? 1 : s === "notinlist" ? 2 : 3
            }

            function matchesSearch(name) {
                var q = search.toLowerCase()
                return q.length === 0 || name.toLowerCase().indexOf(q) === 0
            }
            function buildArray() {
                var src = backend.packs   
                var key = sortKey, dir = sortDir
                var a = []
                for (var i = 0; i < src.length; i++)
                    if (matchesSearch(src[i].name)) a.push(src[i])
                a.sort(function (x, y) {
                    var xv = key === "status" ? packsRoot.statusRank(x.status) : x[key]
                    var yv = key === "status" ? packsRoot.statusRank(y.status) : y[key]
                    var c = xv < yv ? -1 : xv > yv ? 1 : 0
                    if (c === 0) c = x.name < y.name ? -1 : x.name > y.name ? 1 : 0  
                    return dir === "asc" ? c : -c
                })
                return a
            }
            function rebuildModel() {
                packsModel.clear()
                var a = buildArray()
                for (var i = 0; i < a.length; i++)
                    packsModel.append({ name: a[i].name, status: a[i].status, added: a[i].added })
            }



            function reconcile() {
                var src = backend.packs   
                var byName = {}, wantNames = {}, wantCount = 0
                for (var i = 0; i < src.length; i++) {
                    var p = src[i]
                    byName[p.name] = p
                    if (matchesSearch(p.name)) { wantNames[p.name] = true; wantCount++ }
                }
                var structural = (packsModel.count !== wantCount)
                if (!structural)
                    for (var j = 0; j < packsModel.count; j++)
                        if (!wantNames[packsModel.get(j).name]) { structural = true; break }
                if (structural) { rebuildModel(); return }
                for (var k = 0; k < packsModel.count; k++) {
                    var it = packsModel.get(k), bp = byName[it.name]
                    if (!bp) continue
                    if (it.status !== bp.status) packsModel.setProperty(k, "status", bp.status)
                    if (it.added !== bp.added) packsModel.setProperty(k, "added", bp.added)
                }
            }
            function setSort(key) {
                if (key === sortKey) sortDir = (sortDir === "asc" ? "desc" : "asc")
                else { sortKey = key; sortDir = (key === "added" ? "desc" : "asc") }
                backend.setPackSort(sortKey, sortDir)
                rebuildModel()
                packsList.positionViewAtBeginning()   
            }
            onSearchChanged: rebuildModel()
            function isSel(n) { selVer; return selMap[n] === true }
            function toggleSel(n) {
                if (selMap[n]) delete selMap[n]; else selMap[n] = true
                selVer++
            }
            function selNames() {
                var r = []
                for (var k in selMap) if (selMap[k]) r.push(k)
                return r
            }
            function selCount() { selVer; return selNames().length }
            function sortLabelFor(key) {
                for (var i = 0; i < sortDefs.length; i++) if (sortDefs[i].key === key) return sortDefs[i].label
                return key
            }

            Connections {
                target: backend
                function onModsListChanged() {

                    var src = backend.packs
                    var present = {}
                    for (var i = 0; i < src.length; i++) present[src[i].name] = true
                    for (var k in packsRoot.selMap) if (!present[k]) delete packsRoot.selMap[k]
                    packsRoot.selVer++
                    packsRoot.reconcile()
                }
            }
            Component.onCompleted: { backend.reloadMods(); rebuildModel() }


            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                PageHeader {
                    title: root.ui("tab_mods")
                    subtitle: "<b><font color='" + th.text + "'>" + backend.packsActive + "</font></b> "
                              + root.ui("packs_subtitle").replace("{active} ", "").replace("{active}", "")
                                  .replace("{total}", backend.packsCount)
                }

                Item { Layout.fillWidth: true }


                Rectangle {
                    Layout.preferredHeight: 38
                    Layout.preferredWidth: 260
                    radius: th.rBtn
                    color: th.card
                    border.color: searchField.activeFocus ? th.accent : th.cardBorder
                    Behavior on border.color { ColorAnimation { duration: 120 } }
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 13
                        anchors.rightMargin: 10
                        spacing: 8
                        AvIcon { path: ico.search; size: 16; color: th.faint }
                        TextField {
                            id: searchField
                            Layout.fillWidth: true
                            placeholderText: root.ui("manage_search_placeholder")
                            color: th.text
                            placeholderTextColor: th.faint
                            font.family: th.ui; font.pixelSize: 13
                            verticalAlignment: TextInput.AlignVCenter
                            leftPadding: 0; rightPadding: 0; topPadding: 0; bottomPadding: 0
                            background: Item {}
                            selectByMouse: true
                            selectionColor: root.acc(0.35)


                            onTextChanged: searchDebounce.restart()
                            Timer {
                                id: searchDebounce
                                interval: 100
                                onTriggered: packsRoot.search = searchField.text
                            }
                        }
                        AvIcon {
                            visible: searchField.text.length > 0
                            path: ico.plus; size: 14; color: th.mute
                            rotation: 45
                            MouseArea {
                                anchors.fill: parent; anchors.margins: -6
                                cursorShape: Qt.PointingHandCursor
                                onClicked: { searchField.text = ""; searchField.forceActiveFocus() }
                            }
                        }
                    }
                }
                AvButton {
                    kind: "ghost"; size: "sm"; iconPath: ico.refresh
                    text: root.ui("reread_btn")
                    onClicked: backend.reloadMods()
                }
                AvButton {
                    kind: "soft"; size: "sm"; iconPath: ico.plus
                    text: root.ui("add_btn")
                    onClicked: backend.chooseArchives()
                }
            }


            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: th.rLg
                color: th.card
                border.color: th.cardBorder
                clip: true


                readonly property var cols: [38, 30, -1, 150, 132, 56]

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0


                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 44
                        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: th.divider }
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 18
                            anchors.rightMargin: 18
                            spacing: 10
                            Item { Layout.preferredWidth: 38 }
                            Item { Layout.preferredWidth: 30 }

                            Repeater {
                                model: [
                                    { key: "name",   label: root.ui("col_name"),   w: -1 },
                                    { key: "added",  label: root.ui("col_added"),  w: 150 },
                                    { key: "status", label: root.ui("col_status"), w: 132 }
                                ]
                                delegate: Item {
                                    required property var modelData
                                    property bool on: packsRoot.sortKey === modelData.key
                                    Layout.preferredWidth: modelData.w
                                    Layout.fillWidth: modelData.w < 0
                                    Layout.fillHeight: true
                                    RowLayout {
                                        anchors.verticalCenter: parent.verticalCenter
                                        spacing: 6
                                        Text {
                                            text: modelData.label
                                            color: parent.parent.on ? th.text : th.dim
                                            font.family: th.ui; font.pixelSize: 11; font.weight: Font.DemiBold
                                        }
                                        AvIcon {
                                            visible: !parent.parent.on
                                            path: ico.updown; size: 13; color: th.faint; opacity: 0.7
                                        }
                                        AvIcon {
                                            visible: parent.parent.on
                                            path: ico.arrowUp; size: 13; sw: 2; color: th.accent
                                            rotation: packsRoot.sortDir === "asc" ? 0 : 180
                                        }
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: packsRoot.setSort(modelData.key)
                                    }
                                }
                            }
                            Item { Layout.preferredWidth: 56 }
                        }
                    }


                    ListView {
                        id: packsList
                        objectName: "packsList"
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: packsModel
                        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                        delegate: Rectangle {
                            id: packRow
                            required property int index
                            required property string name
                            required property string status
                            required property string added
                            width: packsList.width
                            height: 48
                            property bool checked: packsRoot.isSel(name)
                            color: checked ? root.acc(0.08) : (rowMa.containsMouse ? root.rgba(Qt.rgba(1,1,1,1), 0.03) : "transparent")
                            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: th.rowBorder }

                            MouseArea { id: rowMa; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 18
                                anchors.rightMargin: 18
                                spacing: 10

                                Item {
                                    Layout.preferredWidth: 38
                                    Layout.fillHeight: true
                                    AvCheck {
                                        anchors.verticalCenter: parent.verticalCenter
                                        on: parent.parent.parent.checked
                                        onToggled: packsRoot.toggleSel(name)
                                    }
                                }

                                Text {
                                    Layout.preferredWidth: 30
                                    text: (index + 1 < 10 ? "0" : "") + (index + 1)
                                    color: th.faint
                                    font.family: th.mono; font.pixelSize: 11
                                }

                                Text {
                                    Layout.fillWidth: true
                                    text: name
                                    color: th.text
                                    font.family: th.mono; font.pixelSize: 13
                                    elide: Text.ElideRight
                                }

                                ColumnLayout {
                                    Layout.preferredWidth: 150
                                    spacing: 0
                                    Text {
                                        text: added.split(" ")[0]
                                        color: th.dim
                                        font.family: th.mono; font.pixelSize: 12
                                    }
                                    Text {
                                        text: added.split(" ")[1] || ""
                                        color: th.faint
                                        font.family: th.mono; font.pixelSize: 10
                                    }
                                }

                                Item {
                                    Layout.preferredWidth: 132
                                    Layout.fillHeight: true
                                    AvPill {
                                        anchors.verticalCenter: parent.verticalCenter
                                        status: packRow.status
                                    }
                                }

                                Item {
                                    Layout.preferredWidth: 56
                                    Layout.fillHeight: true
                                    AvToggle {
                                        anchors.verticalCenter: parent.verticalCenter
                                        anchors.right: parent.right
                                        on: status === "active"
                                        onToggled: backend.toggleMod(name)
                                    }
                                }
                            }
                        }
                    }


                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 42
                        Rectangle { anchors.top: parent.top; width: parent.width; height: 1; color: th.divider }
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 18
                            anchors.rightMargin: 18
                            spacing: 8
                            Text {
                                text: packsRoot.selCount() > 0
                                      ? root.ui("footer_selected").replace("{n}", packsRoot.selCount())
                                      : root.ui("footer_summary").replace("{n}", backend.packsCount)
                                             .replace("{key}", packsRoot.sortLabelFor(packsRoot.sortKey))
                                color: th.mute
                                font.family: th.ui; font.pixelSize: 12
                            }
                            AvButton {
                                visible: packsRoot.selCount() > 0
                                kind: "ghost"; size: "sm"; iconPath: ico.power
                                text: root.ui("batch_toggle")
                                Layout.leftMargin: 6
                                onClicked: backend.toggleMods(packsRoot.selNames())
                            }
                            AvButton {
                                visible: packsRoot.selCount() > 0
                                kind: "danger"; size: "sm"; iconPath: ico.trash
                                text: root.ui("manage_remove_btn")
                                onClicked: backend.removeMods(packsRoot.selNames())
                            }
                            Item { Layout.fillWidth: true }
                        }
                    }
                }
            }
        }
    }




    Component {
        id: elsPage
        ColumnLayout {
            id: elsRoot
            objectName: "elsRoot"
            spacing: 16

            property string search: ""


            property var expandMap: ({})
            property int expandVer: 0

            function isExpanded(id) { expandVer; return expandMap[id] === true }
            function toggleExpand(id) {
                if (expandMap[id]) delete expandMap[id]; else expandMap[id] = true
                expandVer++
            }
            function pathsOf(g) {
                var r = []
                for (var i = 0; i < g.files.length; i++) r.push(g.files[i].path)
                return r
            }

            function filterRows(groups, q) {
                if (!q) return groups
                q = q.toLowerCase()
                var out = []
                for (var i = 0; i < groups.length; i++) {
                    var g = groups[i], hit = false
                    for (var j = 0; j < g.files.length; j++)
                        if (g.files[j].name.toLowerCase().indexOf(q) === 0) { hit = true; break }
                    if (hit) out.push(g)
                }
                return out
            }
            function totalFiles(groups) {
                var n = 0
                for (var i = 0; i < groups.length; i++) n += groups[i].count
                return n
            }

            property string sortKey: "added"
            property string sortDir: "desc"
            function setSort(key) {
                if (key === sortKey) sortDir = (sortDir === "asc" ? "desc" : "asc")
                else { sortKey = key; sortDir = (key === "added" ? "desc" : "asc") }
            }
            function sortRows(groups, key, dir) {
                var a = groups.slice()
                a.sort(function (x, y) {
                    var xv = key === "name" ? (x.name || "").toLowerCase() : x.added
                    var yv = key === "name" ? (y.name || "").toLowerCase() : y.added
                    var c = xv < yv ? -1 : xv > yv ? 1 : 0
                    if (c === 0) c = (x.added < y.added ? -1 : x.added > y.added ? 1 : 0)
                    return dir === "asc" ? c : -c
                })
                return a
            }


            property var rows: sortRows(filterRows(backend.elsGroups, search), sortKey, sortDir)


            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                PageHeader {
                    title: root.ui("tab_els")
                    subtitle: backend.elsGroups.length === 1
                              ? root.ui("els_subtitle_one")
                              : root.ui("els_subtitle_many").replace("{n}", backend.elsGroups.length)
                }

                Item { Layout.fillWidth: true }


                Rectangle {
                    Layout.preferredHeight: 38
                    Layout.preferredWidth: 260
                    radius: th.rBtn
                    color: th.card
                    border.color: elsSearchField.activeFocus ? th.accent : th.cardBorder
                    Behavior on border.color { ColorAnimation { duration: 120 } }
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 13
                        anchors.rightMargin: 10
                        spacing: 8
                        AvIcon { path: ico.search; size: 16; color: th.faint }
                        TextField {
                            id: elsSearchField
                            Layout.fillWidth: true
                            placeholderText: root.ui("manage_search_placeholder")
                            color: th.text
                            placeholderTextColor: th.faint
                            font.family: th.ui; font.pixelSize: 13
                            verticalAlignment: TextInput.AlignVCenter
                            leftPadding: 0; rightPadding: 0; topPadding: 0; bottomPadding: 0
                            background: Item {}
                            selectByMouse: true
                            selectionColor: root.acc(0.35)
                            onTextChanged: elsSearchDebounce.restart()
                            Timer {
                                id: elsSearchDebounce
                                interval: 100
                                onTriggered: elsRoot.search = elsSearchField.text
                            }
                        }
                        AvIcon {
                            visible: elsSearchField.text.length > 0
                            path: ico.plus; size: 14; color: th.mute
                            rotation: 45
                            MouseArea {
                                anchors.fill: parent; anchors.margins: -6
                                cursorShape: Qt.PointingHandCursor
                                onClicked: { elsSearchField.text = ""; elsSearchField.forceActiveFocus() }
                            }
                        }
                    }
                }
                AvButton {
                    kind: "ghost"; size: "sm"; iconPath: ico.refresh
                    text: root.ui("reread_btn")
                    onClicked: backend.reloadMods()
                }
                AvButton {
                    kind: "soft"; size: "sm"; iconPath: ico.plus
                    text: root.ui("add_btn")
                    onClicked: backend.chooseArchives()
                }
            }


            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: th.rLg
                color: th.card
                border.color: th.cardBorder
                clip: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0


                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 44
                        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: th.divider }
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 18
                            anchors.rightMargin: 18
                            spacing: 10
                            Item { Layout.preferredWidth: 14 }   
                            Item { Layout.preferredWidth: 18 }   
                            Repeater {
                                model: [
                                    { key: "name",  label: root.ui("col_name"),  w: -1 },
                                    { key: "added", label: root.ui("col_added"), w: 150 }
                                ]
                                delegate: Item {
                                    required property var modelData
                                    property bool on: elsRoot.sortKey === modelData.key
                                    Layout.preferredWidth: modelData.w
                                    Layout.fillWidth: modelData.w < 0
                                    Layout.fillHeight: true
                                    RowLayout {
                                        anchors.left: parent.left
                                        anchors.verticalCenter: parent.verticalCenter
                                        spacing: 6
                                        Text {
                                            text: modelData.label
                                            color: parent.parent.on ? th.text : th.dim
                                            font.family: th.ui; font.pixelSize: 11; font.weight: Font.DemiBold
                                        }
                                        AvIcon {
                                            visible: !parent.parent.on
                                            path: ico.updown; size: 13; color: th.faint; opacity: 0.7
                                        }
                                        AvIcon {
                                            visible: parent.parent.on
                                            path: ico.arrowUp; size: 13; sw: 2; color: th.accent
                                            rotation: elsRoot.sortDir === "asc" ? 0 : 180
                                        }
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: elsRoot.setSort(modelData.key)
                                    }
                                }
                            }
                            Item { Layout.preferredWidth: 110 }
                        }
                    }


                    Item {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        visible: elsRoot.rows.length === 0
                        ColumnLayout {
                            anchors.centerIn: parent
                            spacing: 10
                            AvIcon {
                                Layout.alignment: Qt.AlignHCenter
                                path: ico.folder; size: 34; color: th.faint; opacity: 0.5
                            }
                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: root.ui("els_empty")
                                color: th.mute
                                font.family: th.ui; font.pixelSize: 13
                            }
                        }
                    }


                    ListView {
                        id: elsList
                        objectName: "elsList"
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        visible: elsRoot.rows.length > 0
                        clip: true
                        model: elsRoot.rows
                        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                        delegate: Column {
                            id: groupCol
                            required property var modelData
                            width: elsList.width
                            property bool expanded: elsRoot.isExpanded(modelData.id)


                            Rectangle {
                                width: parent.width
                                height: 48
                                color: headMa.containsMouse ? root.rgba(Qt.rgba(1,1,1,1), 0.03) : "transparent"
                                Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: th.rowBorder }
                                MouseArea {
                                    id: headMa
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: elsRoot.toggleExpand(groupCol.modelData.id)
                                }
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 18
                                    anchors.rightMargin: 18
                                    spacing: 10
                                    AvIcon {
                                        Layout.preferredWidth: 14
                                        path: ico.collapse; size: 13; color: th.faint
                                        rotation: groupCol.expanded ? -90 : 180
                                        Behavior on rotation { NumberAnimation { duration: 130; easing.type: Easing.OutCubic } }
                                    }
                                    AvIcon { path: ico.folder; size: 18; color: th.accent }
                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        Layout.minimumWidth: 0
                                        spacing: 0
                                        Text {
                                            Layout.fillWidth: true
                                            text: groupCol.modelData.name.length > 0
                                                  ? groupCol.modelData.name
                                                  : root.ui("els_group_title").replace("{date}", groupCol.modelData.added.split(" ")[0])
                                            color: th.text
                                            font.family: th.ui; font.pixelSize: 13; font.weight: Font.Medium
                                            elide: Text.ElideRight
                                        }
                                        Text {
                                            Layout.fillWidth: true
                                            text: groupCol.modelData.added
                                            color: th.dim
                                            font.family: th.mono; font.pixelSize: 10
                                            elide: Text.ElideRight
                                        }
                                    }
                                    Text {
                                        Layout.preferredWidth: 150
                                        Layout.alignment: Qt.AlignVCenter
                                        text: root.ui("els_group_count").replace("{n}", groupCol.modelData.count)
                                        color: th.dim
                                        font.family: th.ui; font.pixelSize: 12
                                    }
                                    AvButton {
                                        kind: "danger"; size: "sm"; iconPath: ico.trash
                                        text: root.ui("els_delete_group")
                                        onClicked: backend.removeElsFiles(elsRoot.pathsOf(groupCol.modelData))
                                    }
                                }
                            }


                            Repeater {
                                model: groupCol.expanded ? groupCol.modelData.files : []
                                delegate: Rectangle {
                                    id: fileRow
                                    required property var modelData
                                    width: groupCol.width
                                    height: 40
                                    color: fileMa.containsMouse ? root.rgba(Qt.rgba(1,1,1,1), 0.03)
                                                                : root.rgba(Qt.rgba(0,0,0,1), 0.18)
                                    Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: th.rowBorder }

                                    Rectangle { width: 2; height: parent.height; color: root.acc(0.5); x: 26 }
                                    MouseArea { id: fileMa; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }
                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 50
                                        anchors.rightMargin: 18
                                        spacing: 10
                                        Text {
                                            Layout.fillWidth: true
                                            text: fileRow.modelData.name
                                            color: th.dim
                                            font.family: th.mono; font.pixelSize: 12
                                            elide: Text.ElideRight
                                        }
                                        Text {
                                            Layout.preferredWidth: 150
                                            text: fileRow.modelData.added.split(" ")[1] || ""
                                            color: th.faint
                                            font.family: th.mono; font.pixelSize: 11
                                        }
                                        AvButton {
                                            kind: "ghost"; size: "sm"; iconPath: ico.trash
                                            onClicked: backend.removeElsFiles([fileRow.modelData.path])
                                        }
                                    }
                                }
                            }
                        }
                    }


                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 42
                        Rectangle { anchors.top: parent.top; width: parent.width; height: 1; color: th.divider }
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 18
                            anchors.rightMargin: 18
                            spacing: 8
                            Text {
                                text: backend.elsGroups.length === 1
                                      ? root.ui("els_subtitle_one")
                                      : root.ui("els_subtitle_many").replace("{n}", backend.elsGroups.length)
                                color: th.mute
                                font.family: th.ui; font.pixelSize: 12
                            }
                            Item { Layout.fillWidth: true }
                        }
                    }
                }
            }
        }
    }




    Component {
        id: profilesPage
        ColumnLayout {
            id: profRoot
            objectName: "profRoot"
            spacing: 16


            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                PageHeader {
                    title: root.ui("tab_profiles")
                    subtitle: backend.gtaPathValid
                              ? root.ui("subtitle_placeholder")
                              : root.ui("profile_no_path")
                }
                Item { Layout.fillWidth: true }
            }


            GridView {
                id: profGrid
                objectName: "profGrid"
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                interactive: contentHeight > height
                readonly property int gap: 14
                cellWidth: Math.floor(width / 3)
                cellHeight: Math.floor(cellWidth * 0.60)
                model: backend.profiles.length + 1
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                delegate: Item {
                    id: profCell
                    required property int index
                    width: profGrid.cellWidth
                    height: profGrid.cellHeight

                    readonly property var prof: index > 0 ? backend.profiles[index - 1] : null
                    readonly property color pc: (prof && prof.color && prof.color.length > 0)
                                                ? prof.color : th.accent
                    readonly property bool isActive: prof !== null && prof.active === true


                    Item {
                        id: addTile
                        anchors.fill: parent
                        anchors.rightMargin: profGrid.gap
                        anchors.bottomMargin: profGrid.gap
                        visible: profCell.index === 0
                        opacity: backend.gtaPathValid ? 1 : 0.45
                        property bool hov: addProfMa.containsMouse && backend.gtaPathValid
                        Rectangle {
                            anchors.fill: parent; radius: th.rLg
                            color: addTile.hov ? root.acc(0.06) : "transparent"
                        }
                        DashedBox {
                            anchors.fill: parent
                            stroke: addTile.hov ? th.accent : th.innerBorder
                        }
                        ColumnLayout {
                            anchors.centerIn: parent
                            spacing: 9
                            Rectangle {
                                Layout.alignment: Qt.AlignHCenter
                                width: 46; height: 46; radius: th.rIcon
                                color: addTile.hov ? root.acc(0.15) : th.innerBox
                                AvIcon {
                                    anchors.centerIn: parent; path: ico.plus; size: 22
                                    color: addTile.hov ? th.accent : th.mute
                                }
                            }
                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: root.ui("profiles_new_btn")
                                color: addTile.hov ? th.dim : th.mute
                                font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                            }
                        }
                        MouseArea {
                            id: addProfMa
                            anchors.fill: parent; hoverEnabled: true
                            enabled: backend.gtaPathValid
                            cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
                            onClicked: profileEditor.openNew()
                        }
                    }


                    Rectangle {
                        anchors.fill: parent
                        anchors.rightMargin: profGrid.gap
                        anchors.bottomMargin: profGrid.gap
                        visible: profCell.index > 0
                        radius: th.rLg
                        color: profCell.isActive
                               ? root.rgba(profCell.pc, 0.08)
                               : (tileMa.containsMouse ? Qt.lighter(th.card, 1.25) : th.card)
                        border.width: profCell.isActive ? 1.5 : 1
                        border.color: profCell.isActive ? root.rgba(profCell.pc, 0.55) : th.cardBorder
                        Behavior on color { ColorAnimation { duration: 120 } }


                        MouseArea {
                            id: tileMa
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: if (!profCell.isActive) backend.toggleProfile(profCell.prof.id)
                        }

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 4
                            RowLayout {
                                Layout.fillWidth: true
                                Layout.fillHeight: false
                                spacing: 10
                                Rectangle {
                                    width: 38; height: 38; radius: th.rSm
                                    color: root.rgba(profCell.pc, profCell.isActive ? 0.20 : 0.12)
                                    AvIcon {
                                        anchors.centerIn: parent
                                        path: ico.profiles; size: 18
                                        color: profCell.pc
                                    }
                                }
                                Item { Layout.fillWidth: true }


                                Rectangle {
                                    width: 18; height: 18; radius: 9
                                    color: "transparent"
                                    border.width: 2
                                    border.color: profCell.isActive ? profCell.pc : th.checkBorder
                                    Rectangle {
                                        anchors.centerIn: parent
                                        width: 8; height: 8; radius: 4
                                        color: profCell.pc
                                        visible: profCell.isActive
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        anchors.margins: -4
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: backend.toggleProfile(profCell.prof.id)
                                    }
                                }
                            }
                            Item { Layout.fillHeight: true }
                            Text {
                                Layout.fillWidth: true
                                text: profCell.prof ? profCell.prof.name : ""
                                color: th.textHi
                                font.family: th.ui; font.pixelSize: 14; font.weight: Font.DemiBold
                                elide: Text.ElideRight
                            }
                            Text {
                                Layout.fillWidth: true
                                text: profCell.prof
                                      ? root.ui("profile_count")
                                            .replace("{dlc}", profCell.prof.dlcCount)
                                            .replace("{els}", profCell.prof.elsCount)
                                      : ""
                                color: th.faint
                                font.family: th.mono; font.pixelSize: 11
                                elide: Text.ElideRight
                            }
                            RowLayout {
                                Layout.fillWidth: true
                                Layout.fillHeight: false
                                Layout.topMargin: 6
                                spacing: 6
                                AvButton {
                                    kind: "ghost"; size: "sm"; iconPath: ico.edit
                                    onClicked: profileEditor.openEdit(profCell.prof)
                                }
                                AvButton {
                                    kind: "danger"; size: "sm"; iconPath: ico.trash
                                    onClicked: backend.deleteProfile(profCell.prof.id)
                                }
                                Item { Layout.fillWidth: true }
                            }
                        }
                    }
                }
            }
        }
    }




    Component {
        id: renamePage
        ColumnLayout {
            id: renameRoot
            objectName: "renameRoot"
            spacing: 16


            property string presetId: ""
            function selectedModel() {
                var id = renameRoot.presetId
                var ps = backend.renamePresets
                for (var i = 0; i < ps.length; i++)
                    if (ps[i].id === id) return ps[i].model
                return ""
            }
            function previewName(suffix, ext) {
                var m = selectedModel()
                return m.length > 0 ? m + suffix + ext : root.ui("rename_preview_no_target")
            }

            PageHeader {
                Layout.fillWidth: true
                title: root.ui("tab_rename")
                subtitle: root.ui("subtitle_placeholder")
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 16


                ColumnLayout {
                    Layout.preferredWidth: 56
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 16


                    Item {
                        id: renameDrop
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: 200
                        property bool over: renameDa.containsDrag

                        Rectangle { anchors.fill: parent; radius: th.rLg; color: th.dropBg }
                        Rectangle {
                            anchors.fill: parent; radius: th.rLg
                            visible: renameDrop.over; color: root.acc(0.08)
                        }
                        DashedBox {
                            anchors.fill: parent
                            stroke: renameDrop.over ? th.accent : th.dropDash
                        }
                        ColumnLayout {
                            anchors.centerIn: parent
                            width: parent.width - 32
                            spacing: renameDrop.height < 240 ? 8 : 14
                            Rectangle {
                                Layout.alignment: Qt.AlignHCenter
                                width: 64; height: 64; radius: th.rIcon
                                color: root.acc(0.15)
                                y: renameDrop.over ? -3 : 0
                                scale: renameDrop.over ? 1.04 : 1.0
                                Behavior on y { NumberAnimation { duration: 200 } }
                                Behavior on scale { NumberAnimation { duration: 200 } }
                                AvIcon {
                                    anchors.centerIn: parent
                                    path: ico.rename; size: 28; color: th.accent
                                }
                            }
                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                Layout.fillWidth: true
                                horizontalAlignment: Text.AlignHCenter
                                text: root.ui("rename_drop_headline")
                                color: th.textHi
                                font.family: th.disp; font.pixelSize: 18; font.weight: Font.DemiBold
                                elide: Text.ElideRight
                            }
                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                Layout.fillWidth: true
                                horizontalAlignment: Text.AlignHCenter
                                text: root.ui("rename_drop_formats")
                                color: th.mute
                                font.family: th.mono; font.pixelSize: 12
                                elide: Text.ElideMiddle
                            }
                            RowLayout {
                                Layout.alignment: Qt.AlignHCenter
                                spacing: 9
                                AvButton {
                                    kind: "solid"; iconPath: ico.folder; size: "sm"
                                    text: root.ui("choose_files_btn")
                                    onClicked: backend.renameChooseFiles()
                                }
                                AvButton {
                                    visible: backend.renameGroups.length > 0
                                    kind: "ghost"; iconPath: ico.trash; size: "sm"
                                    text: root.ui("rename_clear_btn")
                                    onClicked: backend.renameClear()
                                }
                            }
                        }
                        DropArea {
                            id: renameDa
                            anchors.fill: parent
                            onDropped: function(drop) {
                                if (drop.hasUrls) backend.renameDrop(drop.urls)
                            }
                        }
                    }


                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: false
                        radius: th.rMd
                        color: th.card
                        border.color: th.cardBorder
                        implicitHeight: detectedCol.implicitHeight
                        ColumnLayout {
                            id: detectedCol
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.top: parent.top
                            spacing: 0
                            Item {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 42
                                Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: th.divider }
                                Text {
                                    anchors.left: parent.left
                                    anchors.leftMargin: 16
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: root.ui("rename_detected_eyebrow")
                                    color: th.dim
                                    font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                                }
                            }
                            ColumnLayout {
                                Layout.fillWidth: true
                                Layout.leftMargin: 16
                                Layout.rightMargin: 16
                                Layout.topMargin: 14
                                Layout.bottomMargin: 16
                                spacing: 6
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 10
                                    Text {
                                        text: backend.renameBase.length > 0
                                              ? backend.renameBase : root.ui("rename_none_short")
                                        color: backend.renameBase.length > 0 ? th.textHi : th.faint
                                        font.family: th.disp; font.pixelSize: 20; font.weight: Font.DemiBold
                                        elide: Text.ElideRight
                                    }
                                    Text {
                                        visible: backend.renameFiles.length > 0
                                        text: root.ui("rename_files_count").replace("{n}", backend.renameFiles.length)
                                        color: th.mute
                                        font.family: th.mono; font.pixelSize: 12
                                    }
                                    Item { Layout.fillWidth: true }
                                }
                                Text {
                                    visible: backend.renameGroups.length > 1
                                    text: root.ui("rename_multi_hint")
                                    color: th.stNotinText
                                    font.family: th.ui; font.pixelSize: 12
                                }
                                Flow {
                                    visible: backend.renameGroups.length > 1
                                    Layout.fillWidth: true
                                    spacing: 7
                                    Repeater {
                                        model: backend.renameGroups
                                        delegate: Rectangle {
                                            required property var modelData
                                            property bool on: backend.renameBase === modelData.base
                                            height: 28
                                            width: chipLbl.implicitWidth + 22
                                            radius: th.rSm
                                            color: on ? root.acc(0.16) : th.ghostBg
                                            border.width: 1
                                            border.color: on ? root.acc(0.4) : th.ghostBorder
                                            Text {
                                                id: chipLbl
                                                anchors.centerIn: parent
                                                text: modelData.base + " · " + modelData.count
                                                color: parent.on ? th.accentText : th.ghostText
                                                font.family: th.mono; font.pixelSize: 12
                                            }
                                            MouseArea {
                                                anchors.fill: parent
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: backend.renameSelectBase(modelData.base)
                                            }
                                        }
                                    }
                                }
                                Text {
                                    visible: backend.renameSkipped > 0
                                    Layout.fillWidth: true
                                    text: root.ui("rename_skipped_note").replace("{n}", backend.renameSkipped)
                                    color: th.mute
                                    font.family: th.ui; font.pixelSize: 11
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                    }


                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: 130
                        radius: th.rLg
                        color: th.card
                        border.color: th.cardBorder
                        clip: true
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 0
                            Item {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 42
                                Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: th.divider }
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 16
                                    anchors.rightMargin: 16
                                    Text {
                                        text: root.ui("rename_preview_label")
                                        color: th.dim
                                        font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                                    }
                                    Item { Layout.fillWidth: true }
                                    Text {
                                        visible: backend.renameFiles.length > 0
                                        text: root.ui("rename_files_count").replace("{n}", backend.renameFiles.length)
                                        color: th.faint
                                        font.family: th.mono; font.pixelSize: 11
                                    }
                                }
                            }
                            Item {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                visible: backend.renameFiles.length === 0
                                Text {
                                    anchors.centerIn: parent
                                    width: parent.width - 36
                                    horizontalAlignment: Text.AlignHCenter
                                    text: root.ui("rename_preview_empty")
                                    color: th.mute
                                    font.family: th.ui; font.pixelSize: 12
                                    wrapMode: Text.WordWrap
                                }
                            }
                            ListView {
                                id: renamePreviewList
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                visible: backend.renameFiles.length > 0
                                clip: true
                                model: backend.renameFiles
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                                delegate: Item {
                                    required property var modelData
                                    width: renamePreviewList.width
                                    height: 34
                                    Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: th.rowBorder }
                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 16
                                        anchors.rightMargin: 16
                                        spacing: 10
                                        Text {
                                            Layout.fillWidth: true
                                            text: modelData.name
                                            color: th.dim
                                            font.family: th.mono; font.pixelSize: 12
                                            elide: Text.ElideMiddle
                                        }
                                        Text {
                                            text: "→"
                                            color: th.faint
                                            font.family: th.mono; font.pixelSize: 12
                                        }
                                        Text {
                                            Layout.fillWidth: true
                                            horizontalAlignment: Text.AlignRight
                                            text: renameRoot.previewName(modelData.suffix, modelData.ext)
                                            color: renameRoot.selectedModel().length > 0 ? th.accentText : th.faint
                                            font.family: th.mono; font.pixelSize: 12
                                            elide: Text.ElideMiddle
                                        }
                                    }
                                }
                            }
                        }
                    }
                }


                ColumnLayout {
                    Layout.preferredWidth: 44
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 16


                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: th.rLg
                        color: th.card
                        border.color: th.cardBorder
                        clip: true
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 0
                            Item {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 48
                                Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: th.divider }
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 16
                                    anchors.rightMargin: 10
                                    Text {
                                        text: root.ui("rename_target_label")
                                        color: th.dim
                                        font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                                    }
                                    Item { Layout.fillWidth: true }
                                    AvButton {
                                        kind: "soft"; size: "sm"; iconPath: ico.plus
                                        text: root.ui("rename_preset_new_btn")
                                        onClicked: renamePresetEditor.openNew()
                                    }
                                }
                            }
                            ListView {
                                id: presetList
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                model: backend.renamePresets
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                                delegate: Rectangle {
                                    id: presetRow
                                    required property var modelData
                                    width: presetList.width
                                    height: 44
                                    property bool on: renameRoot.presetId === modelData.id
                                    color: on ? root.acc(0.10)
                                           : (presetMa.containsMouse ? root.rgba(Qt.rgba(1,1,1,1), 0.03) : "transparent")
                                    Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: th.rowBorder }
                                    MouseArea {
                                        id: presetMa
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: renameRoot.presetId = presetRow.modelData.id
                                    }
                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 16
                                        anchors.rightMargin: 10
                                        spacing: 10
                                        Rectangle {
                                            width: 16; height: 16; radius: 8
                                            color: "transparent"
                                            border.width: 2
                                            border.color: presetRow.on ? th.accent : th.checkBorder
                                            Rectangle {
                                                anchors.centerIn: parent
                                                width: 8; height: 8; radius: 4
                                                color: th.accent; visible: presetRow.on
                                            }
                                        }
                                        Text {
                                            Layout.fillWidth: true
                                            text: presetRow.modelData.name
                                            color: presetRow.on ? th.textHi : th.text
                                            font.family: th.ui; font.pixelSize: 13; font.weight: Font.Medium
                                            elide: Text.ElideRight
                                        }
                                        Text {
                                            text: presetRow.modelData.model
                                            color: th.dim
                                            font.family: th.mono; font.pixelSize: 12
                                        }
                                        AvButton {
                                            kind: "ghost"; size: "sm"; iconPath: ico.edit
                                            onClicked: renamePresetEditor.openEdit(presetRow.modelData)
                                        }
                                    }
                                }
                            }
                        }
                    }





                    Rectangle {
                        id: destCard
                        readonly property bool destMissing: backend.renameDest.length === 0
                                                            && backend.renameNeedsDest
                        Layout.fillWidth: true
                        Layout.fillHeight: false
                        Layout.preferredHeight: 96
                        radius: th.rMd
                        clip: true
                        color: destMissing ? root.rgba(th.stDupDot, 0.06) : th.card
                        border.width: destMissing ? 1.5 : 1
                        border.color: destMissing ? root.rgba(th.stDupDot, 0.55) : th.cardBorder
                        Behavior on border.color { ColorAnimation { duration: 150 } }
                        Behavior on color { ColorAnimation { duration: 150 } }
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 0
                            Item {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 42
                                Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: th.divider }
                                Text {
                                    anchors.left: parent.left
                                    anchors.leftMargin: 16
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: root.ui("rename_dest_eyebrow")
                                    color: th.dim
                                    font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                                }
                            }
                            RowLayout {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Layout.leftMargin: 16
                                Layout.rightMargin: 16
                                spacing: 14
                                Text {
                                    Layout.fillWidth: true
                                    text: backend.renameDest.length > 0 ? backend.renameDest
                                          : destCard.destMissing ? root.ui("rename_dest_missing")
                                          : root.ui("path_unset_short")
                                    color: destCard.destMissing ? th.dangerText : th.dim
                                    font.family: destCard.destMissing ? th.ui : th.mono
                                    font.pixelSize: 12
                                    font.weight: destCard.destMissing ? Font.DemiBold : Font.Normal
                                    elide: Text.ElideMiddle
                                }
                                AvButton {
                                    kind: "ghost"; size: "sm"; iconPath: ico.folder
                                    text: root.ui("change_btn")
                                    onClicked: backend.renameChooseDest()
                                }
                            }
                        }
                    }



                    Rectangle {
                        id: renToast
                        property real frac: -1
                        property bool showDone: false
                        property string prevState: "ready"
                        readonly property bool running: backend.renameState === "running"
                        readonly property bool active: running || showDone
                        Layout.fillWidth: true
                        Layout.fillHeight: false
                        Layout.preferredHeight: active ? 52 : 0
                        Behavior on Layout.preferredHeight {
                            NumberAnimation { duration: 180; easing.type: Easing.OutCubic }
                        }
                        opacity: active ? 1 : 0
                        Behavior on opacity { NumberAnimation { duration: 180 } }
                        visible: opacity > 0.01
                        clip: true
                        radius: th.rMd
                        color: th.card
                        border.color: (showDone && !running) ? root.rgba(th.glyphOk, 0.4) : th.cardBorder

                        Timer {
                            id: renDoneTimer
                            interval: 3500
                            onTriggered: renToast.showDone = false
                        }
                        Connections {
                            target: backend
                            function onProgress(frac, label) {
                                if (renToast.running) renToast.frac = frac
                            }
                            function onRenameChanged() {
                                var s = backend.renameState
                                if (s === "running") {
                                    renToast.showDone = false
                                    renToast.frac = 0
                                } else if (s === "done" && renToast.prevState === "running") {
                                    renToast.showDone = true
                                    renDoneTimer.restart()
                                }
                                renToast.prevState = s
                            }
                        }


                        ColumnLayout {
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.leftMargin: 16
                            anchors.rightMargin: 16
                            spacing: 8
                            visible: renToast.running
                            Text {
                                text: root.ui("rename_running")
                                color: th.dim
                                font.family: th.mono; font.pixelSize: 11
                            }
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 4
                                radius: 2
                                color: th.innerBox
                                Rectangle {
                                    width: parent.width * Math.max(0, Math.min(1, renToast.frac))
                                    height: parent.height; radius: 2; color: th.accent
                                }
                            }
                        }

                        RowLayout {
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.leftMargin: 16
                            anchors.rightMargin: 16
                            spacing: 10
                            visible: !renToast.running && renToast.showDone
                            AvIcon { path: ico.check; size: 16; color: th.glyphOk }
                            Text {
                                Layout.fillWidth: true
                                text: backend.renameSummary
                                color: th.glyphOk
                                font.family: th.ui; font.pixelSize: 13; font.weight: Font.DemiBold
                                elide: Text.ElideRight
                            }
                        }
                    }


                    AvButton {
                        Layout.fillWidth: true
                        kind: "solid"; size: "lg"
                        text: root.ui("rename_execute_btn")
                        enabled: !backend.busy
                                 && backend.renameFiles.length > 0
                                 && renameRoot.selectedModel().length > 0
                                 && (backend.renameDest.length > 0 || !backend.renameNeedsDest)
                        onClicked: backend.renameExecute(renameRoot.selectedModel())
                    }
                }
            }
        }
    }




    Component {
        id: settingsPage
        Flickable {
            id: flick
            contentWidth: width
            contentHeight: settingsCol.implicitHeight
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

            ColumnLayout {
                id: settingsCol
                width: flick.width
                spacing: 18

                PageHeader {
                    Layout.fillWidth: true
                    title: root.ui("tab_settings")
                    subtitle: root.ui("subtitle_placeholder")
                }


                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    Eyebrow { text: root.ui("section_paths") }
                    Rectangle {
                        Layout.fillWidth: true
                        radius: th.rMd
                        color: th.card
                        border.color: th.cardBorder
                        implicitHeight: pathsCol.implicitHeight
                        ColumnLayout {
                            id: pathsCol
                            width: parent.width
                            spacing: 0
                            SettingRow {
                                title: root.ui("row_gta_dir")
                                desc: backend.gtaPath.length > 0 ? backend.gtaPath : root.ui("path_unset_short")
                                control: Component {
                                    AvButton {
                                        kind: "ghost"; size: "sm"; iconPath: ico.folder
                                        text: root.ui("choose_btn")
                                        onClicked: backend.chooseGtaPath()
                                    }
                                }
                            }
                            SettingRow {
                                title: root.ui("row_dlclist")
                                desc: backend.dlclistPath.length > 0 ? backend.dlclistPath : root.ui("path_unset_short")
                                last: true
                                control: Component {
                                    AvButton {
                                        kind: "ghost"; size: "sm"; iconPath: ico.folder
                                        text: root.ui("choose_btn")
                                        onClicked: backend.chooseDlclist()
                                    }
                                }
                            }
                        }
                    }
                }


                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    Eyebrow { text: root.ui("section_behavior") }
                    Rectangle {
                        Layout.fillWidth: true
                        radius: th.rMd
                        color: th.card
                        border.color: th.cardBorder
                        implicitHeight: behCol.implicitHeight
                        ColumnLayout {
                            id: behCol
                            width: parent.width
                            spacing: 0
                            SettingRow {
                                title: root.ui("safebox_title")
                                desc: root.ui("beh_safe_desc")
                                control: Component {
                                    AvToggle {
                                        on: backend.useModsFolder
                                        onToggled: backend.setUseModsFolder(!backend.useModsFolder)
                                    }
                                }
                            }
                            SettingRow {
                                title: root.ui("beh_autox_title")
                                desc: root.ui("beh_autox_desc")
                                control: Component {
                                    AvToggle {
                                        on: backend.autoMaintainDlclist
                                        onToggled: backend.setAutoMaintainDlclist(!backend.autoMaintainDlclist)
                                    }
                                }
                            }
                            SettingRow {
                                title: root.ui("beh_els_title")
                                desc: root.ui("beh_els_desc")
                                control: Component {
                                    AvToggle {
                                        on: backend.detectEls
                                        onToggled: backend.setDetectEls(!backend.detectEls)
                                    }
                                }
                            }
                            SettingRow {
                                title: root.ui("beh_xml_els_title")
                                desc: root.ui("beh_xml_els_desc")
                                control: Component {
                                    AvToggle {
                                        on: backend.renameXmlToEls
                                        onToggled: backend.setRenameXmlToEls(!backend.renameXmlToEls)
                                    }
                                }
                            }
                            SettingRow {
                                title: root.ui("beh_sidebar_auto_title")
                                desc: root.ui("beh_sidebar_auto_desc")
                                last: true
                                control: Component {
                                    AvToggle {
                                        on: backend.sidebarAutoCollapse
                                        onToggled: backend.setSidebarAutoCollapse(!backend.sidebarAutoCollapse)
                                    }
                                }
                            }
                        }
                    }
                }


                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    Eyebrow { text: root.ui("section_zones") }
                    Rectangle {
                        Layout.fillWidth: true
                        radius: th.rMd
                        color: th.card
                        border.color: th.cardBorder
                        implicitHeight: zonesSetCol.implicitHeight
                        ColumnLayout {
                            id: zonesSetCol
                            width: parent.width
                            spacing: 0


                            Item {
                                Layout.fillWidth: true
                                implicitHeight: zonesDescTxt.implicitHeight + 28
                                Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: th.settingRowBorder }
                                Text {
                                    id: zonesDescTxt
                                    anchors.left: parent.left; anchors.right: parent.right
                                    anchors.verticalCenter: parent.verticalCenter
                                    anchors.leftMargin: 18; anchors.rightMargin: 18
                                    text: root.ui("zones_settings_desc")
                                    color: th.mute
                                    font.family: th.ui; font.pixelSize: 12
                                    lineHeight: 1.4
                                    wrapMode: Text.WordWrap
                                }
                            }


                            Repeater {
                                model: backend.dropZones
                                delegate: Item {
                                    required property var modelData
                                    Layout.fillWidth: true
                                    implicitHeight: 58
                                    Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: th.settingRowBorder }
                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 18; anchors.rightMargin: 18
                                        spacing: 12
                                        Rectangle {
                                            width: 12; height: 12; radius: 6
                                            Layout.alignment: Qt.AlignVCenter
                                            color: th.accent
                                        }
                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 2
                                            Text {
                                                text: modelData.name
                                                color: th.text
                                                font.family: th.ui; font.pixelSize: 13; font.weight: Font.Medium
                                                elide: Text.ElideRight; Layout.fillWidth: true
                                            }
                                            Text {
                                                text: modelData.auto ? root.ui("zone_auto_desc")
                                                      : (modelData.rel.length > 0 ? modelData.rel : root.ui("zone_target_root"))
                                                color: th.mute
                                                font.family: modelData.auto ? th.ui : th.mono
                                                font.pixelSize: 11
                                                elide: Text.ElideMiddle; Layout.fillWidth: true
                                            }
                                        }
                                        Text {
                                            text: modelData.w + "×" + modelData.h
                                            color: th.faint
                                            font.family: th.mono; font.pixelSize: 11
                                        }
                                        AvButton {
                                            kind: "ghost"; size: "sm"; iconPath: ico.edit
                                            text: root.ui("zone_edit")
                                            onClicked: zoneEditor.openEdit(modelData)
                                        }
                                        AvButton {
                                            kind: "danger"; size: "sm"; iconPath: ico.trash
                                            onClicked: backend.removeZone(modelData.id)
                                        }
                                    }
                                }
                            }


                            Item {
                                Layout.fillWidth: true
                                implicitHeight: 62
                                function firstFree() {
                                    var z = backend.dropZones
                                    for (var r = 0; r < 2; r++)
                                        for (var c = 0; c < 2; c++) {
                                            var covered = false
                                            for (var i = 0; i < z.length; i++) {
                                                var zz = z[i]
                                                if (c >= zz.col && c < zz.col + zz.w &&
                                                    r >= zz.row && r < zz.row + zz.h) { covered = true; break }
                                            }
                                            if (!covered) return { c: c, r: r }
                                        }
                                    return null
                                }
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 18; anchors.rightMargin: 18
                                    spacing: 9
                                    AvButton {
                                        kind: "soft"; size: "sm"; iconPath: ico.plus
                                        text: root.ui("zones_add")
                                        enabled: backend.dropZones.length < 4 && parent.parent.firstFree() !== null
                                        onClicked: { var f = parent.parent.firstFree(); if (f) zoneEditor.openNew(f.c, f.r) }
                                    }
                                    Text {
                                        visible: !(backend.dropZones.length < 4 && parent.parent.firstFree() !== null)
                                        text: root.ui("zone_grid_full")
                                        color: th.mute
                                        font.family: th.ui; font.pixelSize: 12
                                        Layout.fillWidth: true
                                        wrapMode: Text.WordWrap
                                    }
                                    Item { Layout.fillWidth: true }
                                    AvButton {
                                        kind: "ghost"; size: "sm"; iconPath: ico.refresh
                                        text: root.ui("zones_reset")
                                        onClicked: backend.resetZones()
                                    }
                                }
                            }
                        }
                    }
                }


                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16


                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignTop
                        spacing: 10
                        Eyebrow { text: root.ui("section_language") }
                        Rectangle {
                            Layout.fillWidth: true
                            radius: th.rMd
                            color: th.card
                            border.color: th.cardBorder
                            implicitHeight: langCol.implicitHeight + 16
                            ColumnLayout {
                                id: langCol
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 8
                                spacing: 4
                                Repeater {
                                    model: backend.languages
                                    delegate: Rectangle {
                                        required property var modelData
                                        property bool on: backend.language === modelData.code
                                        Layout.fillWidth: true
                                        implicitHeight: 38
                                        radius: th.rSm
                                        color: on ? root.acc(0.14) : (langMa.containsMouse ? Qt.lighter(th.card, 1.5) : "transparent")
                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.leftMargin: 14
                                            anchors.rightMargin: 14
                                            Text {
                                                text: modelData.label
                                                color: parent.parent.on ? "#ffffff" : th.dim
                                                font.family: th.ui; font.pixelSize: 13; font.weight: Font.Medium
                                                Layout.fillWidth: true
                                            }
                                            AvIcon {
                                                visible: parent.parent.on
                                                path: ico.check; size: 15; sw: 2.4; color: th.accent
                                            }
                                        }
                                        MouseArea {
                                            id: langMa
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: backend.setLanguage(modelData.code)
                                        }
                                    }
                                }
                            }
                        }
                    }


                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignTop
                        spacing: 10
                        Eyebrow { text: root.ui("section_design") }
                        Rectangle {
                            Layout.fillWidth: true
                            radius: th.rMd
                            color: th.card
                            border.color: th.cardBorder
                            implicitHeight: designCol.implicitHeight + 32
                            ColumnLayout {
                                id: designCol
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.margins: 16
                                spacing: 14
                                RowLayout {
                                    spacing: 12
                                    Rectangle {
                                        width: 42; height: 42; radius: th.rSm
                                        color: root.acc(0.18)
                                        AvIcon { anchors.centerIn: parent; path: ico.settings; size: 20; color: th.accent }
                                    }
                                    ColumnLayout {
                                        spacing: 2
                                        Text {
                                            text: root.ui("design_title")
                                            color: th.text
                                            font.family: th.ui; font.pixelSize: 13; font.weight: Font.DemiBold
                                        }
                                        Text {
                                            text: root.ui("design_desc")
                                            color: th.mute
                                            font.family: th.ui; font.pixelSize: 11
                                        }
                                    }
                                    Item { Layout.fillWidth: true }
                                }

                                Flow {
                                    Layout.fillWidth: true
                                    spacing: 8
                                    Repeater {
                                        model: backend.accentPresets
                                        delegate: Rectangle {
                                            required property var modelData
                                            width: 26; height: 26; radius: th.rSm
                                            color: modelData
                                            border.width: 2
                                            border.color: backend.accent.toLowerCase() === modelData.toLowerCase()
                                                          ? "#ffffff" : "transparent"
                                            MouseArea {
                                                anchors.fill: parent
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: backend.setAccent(modelData)
                                            }
                                        }
                                    }
                                    AvButton {
                                        kind: "ghost"; size: "sm"
                                        text: root.ui("settings_accent_custom")
                                        onClicked: backend.pickCustomAccent()
                                    }
                                }
                            }
                        }
                    }
                }


                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    Eyebrow { text: root.ui("section_system") }
                    Rectangle {
                        Layout.fillWidth: true
                        radius: th.rMd
                        color: th.card
                        border.color: th.cardBorder
                        implicitHeight: sysCol.implicitHeight
                        ColumnLayout {
                            id: sysCol
                            width: parent.width
                            spacing: 0
                            SettingRow {
                                title: root.ui("settings_save_history")
                                control: Component {
                                    AvToggle {
                                        on: backend.saveHistory
                                        onToggled: backend.setSaveHistory(!backend.saveHistory)
                                    }
                                }
                            }
                            SettingRow {
                                title: root.ui("settings_check_updates")
                                control: Component {
                                    AvToggle {
                                        on: backend.autoCheck
                                        onToggled: backend.setAutoCheck(!backend.autoCheck)
                                    }
                                }
                            }
                            SettingRow {
                                title: root.ui("settings_version").replace("{version}", backend.version)
                                last: true
                                control: Component {
                                    AvButton {
                                        kind: "ghost"; size: "sm"; iconPath: ico.refresh
                                        text: root.ui("settings_check_now")
                                        onClicked: backend.checkUpdates(true)
                                    }
                                }
                            }
                        }
                    }
                }

                Item { Layout.preferredHeight: 4 }
            }
        }
    }




    component SettingRow: Item {
        id: srow
        property string title: ""
        property string desc: ""
        property bool last: false
        property Component control: null

        Layout.fillWidth: true
        implicitHeight: Math.max(56, txtCol.implicitHeight + 32)

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width; height: 1
            color: th.settingRowBorder
            visible: !srow.last
        }
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 18
            anchors.rightMargin: 18
            spacing: 16
            ColumnLayout {
                id: txtCol
                Layout.fillWidth: true
                spacing: 3
                Text {
                    text: srow.title
                    color: th.text
                    font.family: th.ui; font.pixelSize: 13; font.weight: Font.Medium
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                }
                Text {
                    visible: srow.desc.length > 0
                    text: srow.desc
                    color: th.mute
                    font.family: th.ui; font.pixelSize: 12
                    lineHeight: 1.4
                    Layout.fillWidth: true
                    wrapMode: Text.WrapAnywhere
                }
            }
            Loader {
                sourceComponent: srow.control
                Layout.alignment: Qt.AlignVCenter
            }
        }
    }





    Item {
        id: profileEditor
        objectName: "profileEditor"
        anchors.fill: parent
        z: 1001
        property bool active: false
        property string editId: ""
        property string pcolor: ""               
        property var dlcSel: ({})
        property var elsSel: ({})
        property int selVer: 0
        visible: active


        function flatEls() {
            var g = backend.elsGroups, r = []
            for (var i = 0; i < g.length; i++)
                for (var j = 0; j < g[i].files.length; j++) r.push(g[i].files[j])
            return r
        }
        property var elsFiles: flatEls()

        function isDlc(n) { selVer; return dlcSel[n] === true }
        function isEls(n) { selVer; return elsSel[n] === true }
        function toggleDlc(n) { if (dlcSel[n]) delete dlcSel[n]; else dlcSel[n] = true; selVer++ }
        function toggleEls(n) { if (elsSel[n]) delete elsSel[n]; else elsSel[n] = true; selVer++ }
        function allDlcOn() {
            selVer
            var p = backend.packs
            if (p.length === 0) return false
            for (var i = 0; i < p.length; i++) if (!dlcSel[p[i].name]) return false
            return true
        }
        function allElsOn() {
            selVer
            var f = elsFiles
            if (f.length === 0) return false
            for (var i = 0; i < f.length; i++) if (!elsSel[f[i].name]) return false
            return true
        }
        function setAllDlc(v) {
            var p = backend.packs, m = ({})
            if (v) for (var i = 0; i < p.length; i++) m[p[i].name] = true
            dlcSel = m; selVer++
        }
        function setAllEls(v) {
            var f = elsFiles, m = ({})
            if (v) for (var i = 0; i < f.length; i++) m[f[i].name] = true
            elsSel = m; selVer++
        }
        function openNew() {
            editId = ""
            nameField.text = ""
            pcolor = ""

            dlcSel = ({}); elsSel = ({}); selVer++
            active = true
            nameField.forceActiveFocus()
        }
        function openEdit(prof) {
            editId = prof.id
            nameField.text = prof.name
            pcolor = prof.color || ""
            var dm = ({}), em = ({})
            for (var i = 0; i < prof.dlc.length; i++) dm[prof.dlc[i]] = true
            for (var j = 0; j < prof.els.length; j++) em[prof.els[j]] = true
            dlcSel = dm; elsSel = em; selVer++
            active = true
            nameField.forceActiveFocus()
        }
        function close() { active = false }
        function save() {
            var name = nameField.text.trim()
            if (name.length === 0) { nameField.forceActiveFocus(); return }
            var dlc = [], els = []
            for (var a in dlcSel) if (dlcSel[a]) dlc.push(a)
            for (var b in elsSel) if (elsSel[b]) els.push(b)
            backend.saveProfile(name, dlc, els, pcolor, editId)
            active = false
        }


        Rectangle {
            anchors.fill: parent
            color: root.rgba(Qt.rgba(0, 0, 0, 1), 0.55)
            MouseArea { anchors.fill: parent; hoverEnabled: true; onClicked: profileEditor.close() }
        }


        Rectangle {
            anchors.centerIn: parent
            width: Math.min(580, profileEditor.width - 80)
            height: Math.min(640, profileEditor.height - 80)
            radius: th.rLg
            color: th.card
            border.color: th.cardBorder
            MouseArea { anchors.fill: parent }   

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 22
                spacing: 14

                Text {
                    text: profileEditor.editId.length > 0
                          ? root.ui("profile_editor_edit_title")
                          : root.ui("profile_editor_new_title")
                    color: th.textHi
                    font.family: th.disp; font.pixelSize: 18; font.weight: Font.DemiBold
                }


                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 42
                    radius: th.rBtn
                    color: th.innerBox
                    border.color: nameField.activeFocus ? th.accent : th.innerBorder
                    Behavior on border.color { ColorAnimation { duration: 120 } }
                    TextField {
                        id: nameField
                        anchors.fill: parent
                        anchors.leftMargin: 13; anchors.rightMargin: 13
                        placeholderText: root.ui("profile_name_placeholder")
                        color: th.text
                        placeholderTextColor: th.faint
                        font.family: th.ui; font.pixelSize: 13
                        verticalAlignment: TextInput.AlignVCenter
                        leftPadding: 0; rightPadding: 0; topPadding: 0; bottomPadding: 0
                        background: Item {}
                        selectByMouse: true
                        selectionColor: root.acc(0.35)
                        onAccepted: profileEditor.save()
                    }
                }


                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12
                    Text {
                        text: root.ui("profile_color_label")
                        color: th.dim
                        font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                    }
                    Flow {
                        Layout.fillWidth: true
                        spacing: 7

                        Rectangle {
                            width: 24; height: 24; radius: th.rSm
                            color: th.accent
                            border.width: 2
                            border.color: profileEditor.pcolor.length === 0 ? "#ffffff" : "transparent"
                            MouseArea {
                                anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                onClicked: profileEditor.pcolor = ""
                            }
                        }
                        Repeater {
                            model: backend.accentPresets
                            delegate: Rectangle {
                                required property var modelData
                                width: 24; height: 24; radius: th.rSm
                                color: modelData
                                border.width: 2
                                border.color: profileEditor.pcolor.toLowerCase() === modelData.toLowerCase()
                                              ? "#ffffff" : "transparent"
                                MouseArea {
                                    anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                    onClicked: profileEditor.pcolor = modelData
                                }
                            }
                        }
                    }
                }


                RowLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 12


                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 8
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8
                            Text {
                                text: root.ui("profile_section_dlc")
                                color: th.dim
                                font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                                Layout.fillWidth: true
                            }
                            Text {
                                text: root.ui("profile_select_all")
                                color: th.faint
                                font.family: th.ui; font.pixelSize: 11
                            }
                            AvCheck {
                                size: 16
                                on: profileEditor.allDlcOn()
                                onToggled: profileEditor.setAllDlc(!profileEditor.allDlcOn())
                            }
                        }
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: th.rMd
                            color: th.innerBox
                            border.color: th.innerBorder
                            clip: true
                            Text {
                                anchors.centerIn: parent
                                visible: backend.packs.length === 0
                                text: root.ui("profile_editor_empty")
                                color: th.faint; font.family: th.ui; font.pixelSize: 12
                            }
                            ListView {
                                anchors.fill: parent
                                anchors.margins: 4
                                clip: true
                                model: backend.packs
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                                delegate: Rectangle {
                                    required property var modelData
                                    width: ListView.view.width
                                    height: 34
                                    color: dlcRowMa.containsMouse ? root.rgba(Qt.rgba(1,1,1,1), 0.04) : "transparent"
                                    radius: th.rSm
                                    MouseArea {
                                        id: dlcRowMa
                                        anchors.fill: parent; hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: profileEditor.toggleDlc(modelData.name)
                                    }
                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 10; anchors.rightMargin: 10
                                        spacing: 10
                                        AvCheck {
                                            size: 16
                                            on: profileEditor.isDlc(modelData.name)
                                            onToggled: profileEditor.toggleDlc(modelData.name)
                                        }
                                        Text {
                                            text: modelData.name
                                            color: th.text
                                            font.family: th.mono; font.pixelSize: 12
                                            elide: Text.ElideRight; Layout.fillWidth: true
                                        }
                                    }
                                }
                            }
                        }
                    }


                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 8
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8
                            Text {
                                text: root.ui("profile_section_els")
                                color: th.dim
                                font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                                Layout.fillWidth: true
                            }
                            Text {
                                text: root.ui("profile_select_all")
                                color: th.faint
                                font.family: th.ui; font.pixelSize: 11
                            }
                            AvCheck {
                                size: 16
                                on: profileEditor.allElsOn()
                                onToggled: profileEditor.setAllEls(!profileEditor.allElsOn())
                            }
                        }
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: th.rMd
                            color: th.innerBox
                            border.color: th.innerBorder
                            clip: true
                            Text {
                                anchors.centerIn: parent
                                visible: profileEditor.elsFiles.length === 0
                                text: root.ui("profile_editor_empty")
                                color: th.faint; font.family: th.ui; font.pixelSize: 12
                            }
                            ListView {
                                anchors.fill: parent
                                anchors.margins: 4
                                clip: true
                                model: profileEditor.elsFiles
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                                delegate: Rectangle {
                                    required property var modelData
                                    width: ListView.view.width
                                    height: 34
                                    color: elsRowMa.containsMouse ? root.rgba(Qt.rgba(1,1,1,1), 0.04) : "transparent"
                                    radius: th.rSm
                                    MouseArea {
                                        id: elsRowMa
                                        anchors.fill: parent; hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: profileEditor.toggleEls(modelData.name)
                                    }
                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 10; anchors.rightMargin: 10
                                        spacing: 10
                                        AvCheck {
                                            size: 16
                                            on: profileEditor.isEls(modelData.name)
                                            onToggled: profileEditor.toggleEls(modelData.name)
                                        }
                                        Text {
                                            text: modelData.name
                                            color: th.text
                                            font.family: th.mono; font.pixelSize: 12
                                            elide: Text.ElideRight; Layout.fillWidth: true
                                        }
                                    }
                                }
                            }
                        }
                    }
                }


                RowLayout {
                    Layout.fillWidth: true
                    Layout.topMargin: 2
                    spacing: 9
                    Item { Layout.fillWidth: true }
                    AvButton {
                        kind: "ghost"; text: root.ui("cancel")
                        onClicked: profileEditor.close()
                    }
                    AvButton {
                        kind: "solid"; text: root.ui("profile_save_btn")
                        onClicked: profileEditor.save()
                    }
                }
            }
        }
    }






    Item {
        id: zoneEditor
        objectName: "zoneEditor"
        anchors.fill: parent
        z: 1001
        property bool active: false
        property string editId: ""
        property bool auto: false
        property int layoutIdx: 0
        visible: active




        readonly property var layouts: [
            { col: 0, row: 0, w: 2, h: 2, key: "zone_layout_full" },
            { col: 0, row: 0, w: 2, h: 1, key: "zone_layout_top" },
            { col: 0, row: 1, w: 2, h: 1, key: "zone_layout_bottom" },
            { col: 0, row: 0, w: 1, h: 2, key: "zone_layout_left" },
            { col: 1, row: 0, w: 1, h: 2, key: "zone_layout_right" },
            { col: 0, row: 0, w: 1, h: 1, key: "zone_layout_tl" },
            { col: 1, row: 0, w: 1, h: 1, key: "zone_layout_tr" },
            { col: 0, row: 1, w: 1, h: 1, key: "zone_layout_bl" },
            { col: 1, row: 1, w: 1, h: 1, key: "zone_layout_br" }
        ]


        function cellBusy(c, r) {
            var z = backend.dropZones
            for (var i = 0; i < z.length; i++) {
                var zz = z[i]
                if (zz.id === editId) continue
                if (c >= zz.col && c < zz.col + zz.w && r >= zz.row && r < zz.row + zz.h)
                    return true
            }
            return false
        }
        function layoutFree(l) {
            for (var r = l.row; r < l.row + l.h; r++)
                for (var c = l.col; c < l.col + l.w; c++)
                    if (cellBusy(c, r)) return false
            return true
        }

        function openNew(c, r) {
            editId = ""
            znNameField.text = ""
            znRelField.text = ""
            auto = false
            layoutIdx = 5 + r * 2 + c          
            active = true
            znNameField.forceActiveFocus()
        }
        function openEdit(zone) {
            editId = zone.id
            znNameField.text = zone.name
            znRelField.text = zone.rel
            auto = zone.auto
            layoutIdx = 0
            for (var i = 0; i < layouts.length; i++) {
                var l = layouts[i]
                if (l.col === zone.col && l.row === zone.row && l.w === zone.w && l.h === zone.h) {
                    layoutIdx = i
                    break
                }
            }
            active = true
            znNameField.forceActiveFocus()
        }
        function close() { active = false }
        function save() {
            var l = layouts[layoutIdx]
            if (!layoutFree(l))
                return
            backend.saveZone({
                id: editId,
                name: znNameField.text.trim(),
                auto: auto,
                rel: auto ? "" : znRelField.text.trim(),
                color: "",
                col: l.col, row: l.row, w: l.w, h: l.h
            })
            active = false
        }


        Rectangle {
            anchors.fill: parent
            color: root.rgba(Qt.rgba(0, 0, 0, 1), 0.55)
            MouseArea { anchors.fill: parent; hoverEnabled: true; onClicked: zoneEditor.close() }
        }


        Rectangle {
            anchors.centerIn: parent
            width: Math.min(560, zoneEditor.width - 80)
            height: Math.min(zoneCol.implicitHeight + 44, zoneEditor.height - 60)
            radius: th.rLg
            color: th.card
            border.color: th.cardBorder
            MouseArea { anchors.fill: parent }   

            Flickable {
                anchors.fill: parent
                anchors.margins: 22
                contentWidth: width
                contentHeight: zoneCol.implicitHeight
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                ColumnLayout {
                    id: zoneCol
                    width: parent.width
                    spacing: 16

                    Text {
                        text: zoneEditor.editId.length > 0
                              ? root.ui("zone_editor_edit_title") : root.ui("zone_editor_new_title")
                        color: th.textHi
                        font.family: th.disp; font.pixelSize: 18; font.weight: Font.DemiBold
                    }


                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 42
                        radius: th.rBtn
                        color: th.innerBox
                        border.color: znNameField.activeFocus ? th.accent : th.innerBorder
                        Behavior on border.color { ColorAnimation { duration: 120 } }
                        TextField {
                            id: znNameField
                            anchors.fill: parent
                            anchors.leftMargin: 13; anchors.rightMargin: 13
                            placeholderText: root.ui("zone_name_placeholder")
                            color: th.text
                            placeholderTextColor: th.faint
                            font.family: th.ui; font.pixelSize: 13
                            verticalAlignment: TextInput.AlignVCenter
                            leftPadding: 0; rightPadding: 0; topPadding: 0; bottomPadding: 0
                            background: Item {}
                            selectByMouse: true
                            selectionColor: root.acc(0.35)
                            onAccepted: zoneEditor.save()
                        }
                    }


                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        Text {
                            text: root.ui("zone_mode_label")
                            color: th.dim; font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10
                            Repeater {
                                model: [
                                    { v: true,  t: root.ui("zone_mode_auto"),   d: root.ui("zone_mode_auto_desc") },
                                    { v: false, t: root.ui("zone_mode_custom"), d: root.ui("zone_mode_custom_desc") }
                                ]
                                delegate: Rectangle {
                                    required property var modelData
                                    property bool on: zoneEditor.auto === modelData.v
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 62
                                    radius: th.rMd
                                    color: on ? root.acc(0.12) : th.innerBox
                                    border.width: on ? 1.5 : 1
                                    border.color: on ? th.accent : th.innerBorder
                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 11
                                        spacing: 2
                                        RowLayout {
                                            spacing: 8
                                            AvIcon {
                                                path: modelData.v ? ico.install : ico.folder
                                                size: 15; color: on ? th.accent : th.mute
                                            }
                                            Text {
                                                text: modelData.t
                                                color: on ? th.textHi : th.text
                                                font.family: th.ui; font.pixelSize: 13; font.weight: Font.DemiBold
                                            }
                                        }
                                        Text {
                                            text: modelData.d
                                            color: th.mute
                                            font.family: th.ui; font.pixelSize: 11
                                            Layout.fillWidth: true
                                            wrapMode: Text.WordWrap
                                        }
                                    }
                                    MouseArea {
                                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                        onClicked: zoneEditor.auto = modelData.v
                                    }
                                }
                            }
                        }
                    }


                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        visible: !zoneEditor.auto
                        Text {
                            text: root.ui("zone_target_label")
                            color: th.dim; font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 9
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 42
                                radius: th.rBtn
                                color: th.innerBox
                                border.color: znRelField.activeFocus ? th.accent : th.innerBorder
                                Behavior on border.color { ColorAnimation { duration: 120 } }
                                TextField {
                                    id: znRelField
                                    anchors.fill: parent
                                    anchors.leftMargin: 13; anchors.rightMargin: 13
                                    placeholderText: root.ui("zone_target_root")
                                    color: th.text
                                    placeholderTextColor: th.faint
                                    font.family: th.mono; font.pixelSize: 12
                                    verticalAlignment: TextInput.AlignVCenter
                                    leftPadding: 0; rightPadding: 0; topPadding: 0; bottomPadding: 0
                                    background: Item {}
                                    selectByMouse: true
                                    selectionColor: root.acc(0.35)
                                }
                            }
                            AvButton {
                                kind: "ghost"; size: "sm"; iconPath: ico.folder
                                text: root.ui("zone_browse_btn")
                                onClicked: {
                                    var r = backend.chooseZoneFolder()
                                    if (r !== "") znRelField.text = r
                                }
                            }
                        }

                        Flow {
                            Layout.fillWidth: true
                            spacing: 7
                            visible: backend.zonePresets.length > 0
                            Repeater {
                                model: backend.zonePresets
                                delegate: Rectangle {
                                    required property var modelData
                                    property bool on: znRelField.text === modelData.rel
                                    height: 28
                                    width: presetLbl.implicitWidth + 22
                                    radius: th.rSm
                                    color: on ? root.acc(0.16) : th.ghostBg
                                    border.width: 1
                                    border.color: on ? root.acc(0.4) : th.ghostBorder
                                    Text {
                                        id: presetLbl
                                        anchors.centerIn: parent
                                        text: modelData.label
                                        color: on ? th.accentText : th.ghostText
                                        font.family: th.ui; font.pixelSize: 12; font.weight: Font.Medium
                                    }
                                    MouseArea {
                                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                                        onClicked: znRelField.text = modelData.rel
                                    }
                                }
                            }
                        }
                    }




                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        Text {
                            text: root.ui("zone_layout_label")
                            color: th.dim; font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                        }
                        Grid {
                            id: layoutGrid
                            columns: 3
                            spacing: 8
                            readonly property real tileW: (zoneCol.width - 16) / 3
                            Repeater {
                                model: zoneEditor.layouts.length
                                delegate: Rectangle {
                                    id: layTile
                                    required property int index
                                    readonly property var lay: zoneEditor.layouts[index]
                                    readonly property bool free: zoneEditor.layoutFree(lay)
                                    readonly property bool on: zoneEditor.layoutIdx === index
                                    width: layoutGrid.tileW
                                    height: 72
                                    radius: th.rSm
                                    color: on ? root.acc(0.12) : (layMa.containsMouse && free ? Qt.lighter(th.innerBox, 1.4) : th.innerBox)
                                    border.width: on ? 1.5 : 1
                                    border.color: on ? th.accent : th.innerBorder
                                    opacity: free ? 1 : 0.35
                                    ColumnLayout {
                                        anchors.centerIn: parent
                                        spacing: 6
                                        Grid {
                                            Layout.alignment: Qt.AlignHCenter
                                            columns: 2
                                            spacing: 3
                                            Repeater {
                                                model: [
                                                    { c: 0, r: 0 }, { c: 1, r: 0 },
                                                    { c: 0, r: 1 }, { c: 1, r: 1 }
                                                ]
                                                delegate: Rectangle {
                                                    required property var modelData
                                                    readonly property bool inLay:
                                                        modelData.c >= layTile.lay.col && modelData.c < layTile.lay.col + layTile.lay.w &&
                                                        modelData.r >= layTile.lay.row && modelData.r < layTile.lay.row + layTile.lay.h
                                                    width: 19; height: 12
                                                    radius: 2
                                                    color: inLay ? (layTile.on ? th.accent : th.dim) : "transparent"
                                                    border.width: inLay ? 0 : 1
                                                    border.color: th.checkBorder
                                                }
                                            }
                                        }
                                        Text {
                                            Layout.alignment: Qt.AlignHCenter
                                            text: root.ui(layTile.lay.key)
                                            color: layTile.on ? th.accentText : th.mute
                                            font.family: th.ui; font.pixelSize: 10; font.weight: Font.Medium
                                        }
                                    }
                                    MouseArea {
                                        id: layMa
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        enabled: layTile.free
                                        cursorShape: layTile.free ? Qt.PointingHandCursor : Qt.ArrowCursor
                                        onClicked: zoneEditor.layoutIdx = layTile.index
                                    }
                                }
                            }
                        }
                    }


                    RowLayout {
                        Layout.fillWidth: true
                        Layout.topMargin: 2
                        spacing: 9
                        AvButton {
                            visible: zoneEditor.editId.length > 0
                            kind: "danger"; iconPath: ico.trash; text: root.ui("zone_delete_btn")
                            onClicked: { backend.removeZone(zoneEditor.editId); zoneEditor.close() }
                        }
                        Item { Layout.fillWidth: true }
                        AvButton {
                            kind: "ghost"; text: root.ui("cancel")
                            onClicked: zoneEditor.close()
                        }
                        AvButton {
                            kind: "solid"; text: root.ui("zone_save_btn")
                            enabled: zoneEditor.layoutFree(zoneEditor.layouts[zoneEditor.layoutIdx])
                            onClicked: zoneEditor.save()
                        }
                    }
                }
            }
        }
    }





    Item {
        id: renamePresetEditor
        objectName: "renamePresetEditor"
        anchors.fill: parent
        z: 1001
        property bool active: false
        property string editId: ""
        visible: active

        function openNew() {
            editId = ""
            rpNameField.text = ""
            rpModelField.text = ""
            active = true
            rpNameField.forceActiveFocus()
        }
        function openEdit(preset) {
            editId = preset.id
            rpNameField.text = preset.name
            rpModelField.text = preset.model
            active = true
            rpNameField.forceActiveFocus()
        }
        function close() { active = false }
        function save() {
            var name = rpNameField.text.trim()
            var model = rpModelField.text.trim()
            if (name.length === 0) { rpNameField.forceActiveFocus(); return }
            if (model.length === 0) { rpModelField.forceActiveFocus(); return }
            backend.saveRenamePreset({ id: editId, name: name, model: model })
            active = false
        }


        Rectangle {
            anchors.fill: parent
            color: root.rgba(Qt.rgba(0, 0, 0, 1), 0.55)
            MouseArea { anchors.fill: parent; hoverEnabled: true; onClicked: renamePresetEditor.close() }
        }


        Rectangle {
            anchors.centerIn: parent
            width: Math.min(440, renamePresetEditor.width - 80)
            implicitHeight: rpCol.implicitHeight + 44
            radius: th.rLg
            color: th.card
            border.color: th.cardBorder
            MouseArea { anchors.fill: parent }   

            ColumnLayout {
                id: rpCol
                anchors.fill: parent
                anchors.margins: 22
                spacing: 14

                Text {
                    text: renamePresetEditor.editId.length > 0
                          ? root.ui("rename_preset_editor_edit_title")
                          : root.ui("rename_preset_editor_new_title")
                    color: th.textHi
                    font.family: th.disp; font.pixelSize: 18; font.weight: Font.DemiBold
                }


                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    Text {
                        text: root.ui("rename_preset_name_label")
                        color: th.dim; font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 42
                        radius: th.rBtn
                        color: th.innerBox
                        border.color: rpNameField.activeFocus ? th.accent : th.innerBorder
                        Behavior on border.color { ColorAnimation { duration: 120 } }
                        TextField {
                            id: rpNameField
                            anchors.fill: parent
                            anchors.leftMargin: 13; anchors.rightMargin: 13
                            placeholderText: root.ui("rename_preset_name_placeholder")
                            color: th.text
                            placeholderTextColor: th.faint
                            font.family: th.ui; font.pixelSize: 13
                            verticalAlignment: TextInput.AlignVCenter
                            leftPadding: 0; rightPadding: 0; topPadding: 0; bottomPadding: 0
                            background: Item {}
                            selectByMouse: true
                            selectionColor: root.acc(0.35)
                            onAccepted: renamePresetEditor.save()
                        }
                    }
                }


                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    Text {
                        text: root.ui("rename_preset_model_label")
                        color: th.dim; font.family: th.ui; font.pixelSize: 12; font.weight: Font.DemiBold
                    }
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 42
                        radius: th.rBtn
                        color: th.innerBox
                        border.color: rpModelField.activeFocus ? th.accent : th.innerBorder
                        Behavior on border.color { ColorAnimation { duration: 120 } }
                        TextField {
                            id: rpModelField
                            anchors.fill: parent
                            anchors.leftMargin: 13; anchors.rightMargin: 13
                            placeholderText: root.ui("rename_preset_model_placeholder")
                            color: th.text
                            placeholderTextColor: th.faint
                            font.family: th.mono; font.pixelSize: 12
                            verticalAlignment: TextInput.AlignVCenter
                            leftPadding: 0; rightPadding: 0; topPadding: 0; bottomPadding: 0
                            background: Item {}
                            selectByMouse: true
                            selectionColor: root.acc(0.35)
                            onAccepted: renamePresetEditor.save()
                        }
                    }
                }


                RowLayout {
                    Layout.fillWidth: true
                    Layout.topMargin: 2
                    spacing: 9
                    AvButton {
                        visible: renamePresetEditor.editId.length > 0
                        kind: "danger"; iconPath: ico.trash; text: root.ui("zone_delete_btn")
                        onClicked: {
                            backend.removeRenamePreset(renamePresetEditor.editId)
                            renamePresetEditor.close()
                        }
                    }
                    Item { Layout.fillWidth: true }
                    AvButton {
                        kind: "ghost"; text: root.ui("cancel")
                        onClicked: renamePresetEditor.close()
                    }
                    AvButton {
                        kind: "solid"; text: root.ui("rename_preset_save_btn")
                        onClicked: renamePresetEditor.save()
                    }
                }
            }
        }
    }






    Item {
        id: dlg
        objectName: "dlg"
        anchors.fill: parent
        z: 1000
        property var spec: null
        property bool active: spec !== null
        property string selValue: ""
        visible: active

        function open(s) {
            selValue = (s && s.selected) ? s.selected : ""
            spec = s
            dlgFocus.forceActiveFocus()
        }
        function resolve(id) { spec = null; backend.resolveDialog(id) }
        function dismiss() { resolve(spec && spec.cancelId ? spec.cancelId : "") }
        function accept() {
            if (!spec) return
            if (spec.template === "picker") { resolve(selValue); return }
            var b = spec.buttons
            if (b && b.length) resolve(b[b.length - 1].id)   
        }

        Connections {
            target: backend
            function onDialogRequested(s) { dlg.open(s) }
        }


        Rectangle {
            anchors.fill: parent
            color: root.rgba(Qt.rgba(0, 0, 0, 1), 0.55)
            MouseArea { anchors.fill: parent; hoverEnabled: true; onClicked: dlg.dismiss() }
        }


        FocusScope {
            id: dlgFocus
            anchors.fill: parent
            Keys.onEscapePressed: dlg.dismiss()
            Keys.onReturnPressed: dlg.accept()
            Keys.onEnterPressed: dlg.accept()
        }


        Rectangle {
            anchors.centerIn: parent
            width: Math.min(460, dlg.width - 80)
            implicitHeight: cardCol.implicitHeight + 44
            radius: th.rLg
            color: th.card
            border.color: th.cardBorder
            MouseArea { anchors.fill: parent }   

            ColumnLayout {
                id: cardCol
                anchors.fill: parent
                anchors.margins: 22
                spacing: 14

                Text {
                    visible: text.length > 0
                    text: dlg.spec ? dlg.spec.title : ""
                    color: th.textHi
                    font.family: th.disp; font.pixelSize: 18; font.weight: Font.DemiBold
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                }
                Text {
                    visible: text.length > 0
                    text: dlg.spec ? dlg.spec.body : ""
                    color: th.dim
                    font.family: th.ui; font.pixelSize: 13
                    lineHeight: 1.35
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    textFormat: Text.StyledText
                }


                Rectangle {
                    visible: dlg.spec && dlg.spec.template === "picker"
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.min(280, pickList.contentHeight + 2)
                    radius: th.rMd
                    color: th.innerBox
                    border.color: th.innerBorder
                    clip: true
                    ListView {
                        id: pickList
                        anchors.fill: parent
                        anchors.margins: 1
                        model: (dlg.spec && dlg.spec.template === "picker") ? dlg.spec.options : []
                        clip: true
                        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                        delegate: Rectangle {
                            id: pickRow
                            required property var modelData
                            width: pickList.width
                            height: 46
                            property bool sel: dlg.selValue === modelData.value
                            color: pickRow.sel ? root.acc(0.12)
                                   : (pmMa.containsMouse ? root.rgba(Qt.rgba(1,1,1,1), 0.03) : "transparent")
                            MouseArea {
                                id: pmMa
                                anchors.fill: parent; hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: dlg.selValue = pickRow.modelData.value
                            }
                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 14; anchors.rightMargin: 14
                                spacing: 11
                                Rectangle {
                                    width: 16; height: 16; radius: 8
                                    color: "transparent"
                                    border.width: 2
                                    border.color: pickRow.sel ? th.accent : th.checkBorder
                                    Rectangle {
                                        anchors.centerIn: parent
                                        width: 8; height: 8; radius: 4
                                        color: th.accent; visible: pickRow.sel
                                    }
                                }
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 1
                                    Text {
                                        text: pickRow.modelData.label
                                        color: th.text; font.family: th.ui; font.pixelSize: 13
                                        elide: Text.ElideRight; Layout.fillWidth: true
                                    }
                                    Text {
                                        visible: text.length > 0
                                        text: pickRow.modelData.note || ""
                                        color: th.faint; font.family: th.ui; font.pixelSize: 11
                                        elide: Text.ElideRight; Layout.fillWidth: true
                                    }
                                }
                            }
                        }
                    }
                }


                RowLayout {
                    Layout.fillWidth: true
                    Layout.topMargin: 2
                    spacing: 9
                    Item { Layout.fillWidth: true }
                    Repeater {
                        model: (dlg.spec && dlg.spec.template === "message") ? dlg.spec.buttons : []
                        delegate: AvButton {
                            required property var modelData
                            kind: modelData.kind || "ghost"
                            text: modelData.label
                            onClicked: dlg.resolve(modelData.id)
                        }
                    }
                    AvButton {
                        visible: dlg.spec && dlg.spec.template === "picker"
                        kind: "ghost"; text: root.ui("cancel")
                        onClicked: dlg.resolve("")
                    }
                    AvButton {
                        visible: dlg.spec && dlg.spec.template === "picker"
                        kind: "solid"; text: root.ui("ok")
                        onClicked: dlg.resolve(dlg.selValue)
                    }
                }
            }
        }
    }

    onClosing: backend.saveOnClose()

    Component.onCompleted: { backend.promptInitialLanguage(); backend.maybeCheckOnStart() }
}
