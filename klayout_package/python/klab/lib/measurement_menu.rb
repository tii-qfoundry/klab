# KLayout Ruby script to create the 'Measurement' menu.
# This script will be loaded by KLayout on startup.

module MeasurementPlugin

  class MenuHandler
  
    # This method is called when the menu is created the first time.
    def menu_loaded
    
      # Get the main window instance.
      mw = RBA::Application.instance.main_window
      
      # Create a new menu called "Measurement" before the "Help" menu.
      # The "Help" menu has the object name "help_menu".
      menu = mw.menu.insert_menu("help_menu", "measurement_menu", "Measurement")
      
      # Add a "Setup" action to this menu.
      # The action is calling the 'setup_triggered' method in this instance.
      action = RBA::Action.new
      action.title = "Setup Measurement"
      action.on_triggered do 
        self.setup_triggered
      end
      menu.add_item(action)
      
      # Add a "Run" action to this menu.
      # The action is calling the 'run_triggered' method in this instance.
      action = RBA::Action.new
      action.title = "Run Measurement"
      action.on_triggered do 
        self.run_triggered
      end
      menu.add_item(action)
      
    end

    # This is the handler for the "Setup" action.
    def setup_triggered
      RBA::MessageBox.info("Setup", "Setup Measurement triggered (Ruby). This will eventually open a Python-driven dialog.", RBA::MessageBox.b_ok)
      # Here we will eventually call our Python code to show the measurement tab.
    end
    
    # This is the handler for the "Run" action.
    def run_triggered
      RBA::MessageBox.info("Run", "Run Measurement triggered (Ruby). This will eventually start the measurement process.", RBA::MessageBox.b_ok)
      # Here we will eventually call our Python code to start the measurement.
    end

  end

  # Instantiate the handler.
  # The instance is kept in a global variable to prevent it from being garbage-collected.
  $measurement_menu_handler = MenuHandler.new

  # Register a menu listener that calls the 'menu_loaded' method on the
  # handler instance.
  # The listener is registered with a description that is not used further.
  RBA::Application.instance.main_window.add_menu_item_insert_listener("measurement_menu_listener") do
    $measurement_menu_handler.menu_loaded
  end

end
