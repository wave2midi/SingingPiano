import QtQuick 2.12
import SingingpianoGUIVersion 1.0
import QtQuick.Studio.Effects 1.0
import QtQuick.Controls 2.3
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2




Rectangle {
    width: Constants.width
    height: Constants.height
    id: rectangle
    color: "#a7c0cd"
    anchors.fill: parent


    signal outputSignal(string text)
    onOutputSignal:{
                outputArea.text = text
            }
    FileDialog{
        id:browsewindow
        visible:false
        title:"Choose a file to convert..."
        //folder: shortcuts.document
        selectExisting:true
        selectFolder:false
        selectMultiple:true
        nameFilters: ["Wave PCM (*.wav)", "Mel-Scaled Audio (*.mela)"]
        onAccepted: {
            console.log("qml:file selected")
            wavpath.text=browsewindow.fileUrl
        }
        onRejected: {
            console.log("qml:file canceled")
            //Qt.quit()
        }
    }
	MessageDialog{
        id:bfinput
        visible:false
        title:"Choose a file to convert..."
        //folder: shortcuts.document
		
        onAccepted: {
            console.log("qml:custom basicgreq. selected")
			comboBox.model = [bfinputfield.text,con.getSF(0),con.getSF(1),con.getSF(2)]
			bfinput.visible = false
		}
            
        onRejected: {
            console.log("qml:custom basicfreq. canceled")
            //Qt.quit()
        }
		ColumnLayout {
				TextField {
                    id: bfinputfield
                    text: qsTr("440")
                    Layout.preferredHeight: global.height / 480 * 50
                    Layout.preferredWidth: parent.width
                    //Layout.preferredWidth: global.width/640*106
                }
				Button {
                id: bfbutton
                text: "OK"
                onClicked:{
                    bfinput.accepted()
                }
				}
		}
    }
    ColumnLayout {
        id: global
        objectName: "global"
        scale: 0.95
        anchors.fill: parent

        Text {
            id: hint1
            //anchors.left: parent
            text: "Waveform file path"
            Layout.preferredHeight: global.height / 480 * 12
            Layout.preferredWidth: global.width

            font.pixelSize: 15
        }

        RowLayout {
            Layout.preferredHeight: global.height / 480 * 48
            Layout.preferredWidth: global.width
            TextField {
                id: wavpath
                text: "Browse of type the path to file..."
                Layout.preferredWidth: global.width - button1.width
            }

            Button {
                id: button1
                text: "Browse..."
                onClicked:{
                    console.log("qml:browse.clicked")
                    browsewindow.visible=true
                }
            }
        }

        RowLayout {
            Layout.preferredHeight: global.height / 480 * 12
            Text {
                id: element2
                text: qsTr("Min. velocity for notes")

                Layout.preferredWidth: 200
                font.pixelSize: 15
            }

            Text {
                id: element
                text: qsTr("Pitch standard (A=)")

                Layout.preferredWidth: global.width - element2.width
                font.pixelSize: 15
            }
        }

        RowLayout {
            Layout.preferredHeight: global.height / 480 * 140
            Layout.preferredWidth: global.width
            ColumnLayout {
                id: cl3
                Layout.alignment:  Qt.AlignTop
                Layout.preferredWidth: 200
                Slider {
                    from: 0
                    to: 64
                    stepSize: 1
                    id: slider
                    Layout.alignment:  Qt.AlignTop
                    Layout.preferredWidth: 200
                
                    value: 0
                    onValueChanged:{
                        sliderIndi.text = slider.value.toString()
                    }
                }
                Text {
                    id: sliderIndi
                    text: qsTr("0")
                    font.pixelSize: 15
                }

            }
            ColumnLayout {
                id: cl1
                Layout.alignment:  Qt.AlignTop
                Layout.preferredWidth: global.width / 640 * 106
                ComboBox {
                    id: comboBox
                    Layout.preferredHeight: global.height / 480 * 42
                    Layout.preferredWidth: parent.width
					onActivated:{
					if(comboBox.currentText==con.t("generic.option.freq_value_custom")){
						
						bfinput.visible = true
						
						
					}
					}
                }

                Text {
                    id: element4
                    text: qsTr("Tempo")
                    Layout.preferredHeight: global.height / 480 * 9
                    Layout.preferredWidth: parent.width
                    font.pixelSize: 15
                }

                TextField {
                    id: textField
                    text: qsTr("500")
                    Layout.preferredHeight: global.height / 480 * 50
                    Layout.preferredWidth: parent.width
                    //Layout.preferredWidth: global.width/640*106
                }
            }

            ColumnLayout {
                Layout.alignment:  Qt.AlignTop
                Layout.preferredHeight: global.height / 480 * 96
                Layout.preferredWidth: global.width - cl1.width - slider.width
                CheckBox {
                    id: checkBox
                    text: qsTr("Use pitchwheel to mod freq.")
                    Layout.preferredHeight: global.height / 480 * 48
                    Layout.preferredWidth: 250
                    checked:true
                }

                CheckBox {
                    id: checkBox1
                    text: qsTr("Use recorder in MIDI output")
					Layout.preferredHeight: global.height / 480 * 48
                    Layout.preferredWidth: 250
                    checked:true
                    enabled:false
                }
            }
        }

        Text {
            id: hint3
            text: qsTr("Output")
            Layout.preferredHeight: global.height / 480 * 12
            Layout.preferredWidth: global.width
            font.pixelSize: 15
        }
        Flickable{
            id:flickable
            objectName: "Flickable"
            clip:true
            Layout.preferredHeight: global.height / 480*153
            Layout.preferredWidth: global.width
            contentWidth: global.width
            contentHeight: global.height / 480*153
            ScrollBar.vertical: ScrollBar{
                id:vbar
                active:vbar.active
            }
            TextArea.flickable: TextArea {
                id: outputArea
                objectName: "output"
                text: qsTr("...")
                wrapMode: Text.WordWrap
                property double value: 0.0
                onValueChanged:{
                    if(outputArea.value==1.0){
                        outputArea.value=0.0
                        outputArea.text=con.getBufferTextFull()
                    }
                }
            
        }
        }


        ProgressBar {
            id: progressBar
            objectName: "ProgressBar"
            Layout.preferredHeight: global.height / 480*12
            Layout.preferredWidth: global.width
            value: 0.0
        }

        RowLayout {
            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
            id:buttons
            objectName: "buttons"
			Text {
				id: tiderc
				anchors.left: parent
				text: ""
				Layout.preferredHeight: global.height / 480 * 12
				Layout.preferredWidth: global.width-button.width-button2.width

				font.pixelSize: 15
			}
            Button {
                id: button
                text: qsTr("Convert to Equal-Tempered Data")
                Layout.preferredHeight: global.height / 480*48
                //Layout.preferredWidth: 200
                onClicked:{
                    buttons.enabled=false
                    console.log("qml:converting to DFTData")
                    con.wave2DataWithoutProgressbar(wavpath.text,comboBox.currentText,textField.text,slider.value,checkBox.checked)
                }
            }

            Button {
                id: button2
                text: qsTr("Convert to MIDI")
                Layout.preferredHeight: global.height / 480*48
                //Layout.preferredWidth: 200
                onClicked:{
                    buttons.enabled=false
                    console.log("qml:converting to midi")
                    con.wave2MIDIWithoutProgressbar(wavpath.text,comboBox.currentText,textField.text,slider.value,checkBox.checked)
                }
            }
        }
    }
	Component.onCompleted: {
		outputArea.text=""
        //
        ///*
        button.text=con.t("generic.operation.convert_to_dft128")
        button2.text=con.t("generic.operation.convert_to_midi")
        hint3.text=con.t("generic.title.output")
        checkBox1.text=con.t("generic.option.pchange_recorder")
        checkBox.text=con.t("generic.option.pitchwheel")
        element4.text=con.t("generic.title.tempo")
        element.text=con.t("generic.option.freq.standard")
        element2.text=con.t("generic.option.velocitylimit_min")
        button1.text=con.t("generic.operation.browse")
        hint1.text=con.t("generic.title.wavpath")
        wavpath.text=con.t("generic.option.wavpath")
        browsewindow.title=con.t("generic.filechooser.hint")
        sliderIndi.text=slider.value.toString()
        //*/
		tiderc.text=con.getT()
        ////
        comboBox.model = [con.getSF(0),con.getSF(1),con.getSF(2),con.t("generic.option.freq_value_custom")]
        //console.log(con.getSF())
	}
}

/*##^##
Designer {
    D{i:2;anchors_x:32;anchors_y:18}D{i:1;anchors_height:480;anchors_width:640}
}
##^##*/

