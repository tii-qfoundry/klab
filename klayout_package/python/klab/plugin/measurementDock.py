# ==================================================================
# This file contains the implementation of the main measurement
# dockable widget (the "Measurement" tab).
# ==================================================================

import pya

class MeasurementDock(pya.QDockWidget):
    def __init__(self, parent=None):
        super(MeasurementDock, self).__init__("Measurement", parent)
        
        self.main_widget = pya.QWidget(self)
        self.setWidget(self.main_widget)
        
        self.main_layout = pya.QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        
        # --- Create UI Controls ---
        self.measure_button = pya.QPushButton("Measure Selected Cell", self.main_widget)
        self.measure_button.clicked(self._on_measure_clicked)
        
        self.info_label = pya.QLabel("Select a measurement PCell in the layout and click the button.", self.main_widget)
        self.info_label.word_wrap = True
        self.info_label.setAlignment(pya.Qt.AlignHCenter)
        
        # --- NEW: Add a group box to display the result ---
        self.results_group = pya.QGroupBox("Last Measurement Result")
        self.results_layout = pya.QVBoxLayout()
        self.results_group.setLayout(self.results_layout)
        
        self.result_label = pya.QLabel("Result: --")
        font = self.result_label.font
        font.bold = True
        self.result_label.font = font
        self.results_layout.addWidget(self.result_label)
        
        # --- Add widgets to the main layout ---
        self.main_layout.addWidget(self.measure_button)
        self.main_layout.addWidget(self.info_label)
        self.main_layout.addWidget(self.results_group)
        self.main_layout.addStretch(1) # Spacer

    def _on_measure_clicked(self):
        """
        This method is called when the 'Measure Selected Cell' button is clicked.
        It runs the measurement and updates the result label in this dock.
        """
        app = pya.Application.instance()
        mw = app.main_window()
        view = mw.current_view()
        if view is None: return

        selection = view.object_selection
        if len(selection) != 1:
            mw.message("Please select exactly one measurement cell.", 2000)
            return

        instance = selection[0].inst()
        if not instance.is_pcell():
            mw.message("The selected object is not a PCell.", 2000)
            return

        pcell_declaration = instance.pcell_declaration()
        
        if hasattr(pcell_declaration, '_run_measurement'):
            
            # STEP 1: Sync parameters FROM instance TO declaration
            instance_params_by_name = instance.pcell_parameters_by_name()
            for name, value in instance_params_by_name.items():
                setattr(pcell_declaration, name, value)

            # STEP 2: Run the measurement
            pcell_declaration._run_measurement()
            
            # --- NEW: Update the result label in the dock ---
            self.result_label.text = f"Result: {pcell_declaration.value}"
            print(f"Updated result label in dock to: {pcell_declaration.value}")

            # --- STEP 3: Attempt to update the PCell (existing logic) ---
            try:
                view.transaction("Update PCell Measurement Value")
                param_declarations = pcell_declaration.get_parameters()
                new_values_list = []
                for p_decl in param_declarations:
                    if p_decl.name == "value":
                        new_values_list.append(pcell_declaration.value)
                    else:
                        new_values_list.append(instance_params_by_name[p_decl.name])
                
                instance.pcell_parameters = new_values_list
                view.commit()
                mw.message(f"Measurement complete: {pcell_declaration.value}", 3000)
            except Exception as e:
                print(f"An error occurred during PCell update transaction: {e}")
                #app.rollback()
            
        else:
            mw.message("The selected PCell is not a supported measurement cell.", 2000)