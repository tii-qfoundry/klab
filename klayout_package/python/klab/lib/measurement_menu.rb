module KLab
  # This module defines the main menu for the KLab plugin
  class Menu
    def self.setup
      app = RBA::Application.instance
      mw = app.main_window

      # --- Create the main "KLab" menu ---
      # This menu will hold general actions like the reloader.
      # The measurement-specific button is now inside the dock widget.
      menu = mw.menu.find_menu("klab.menu") || mw.menu.insert_menu("klab.menu.end", "KLab", "KLab Tools")

      # --- Call Python to set up the UI ---
      # This will create and show the dockable "Measurement" tab with its button.
      pya_script = "from klab.plugin.menu import setup_plugin; setup_plugin()"
      mw.exec_pya_script(pya_script)
      
    end
  end

  Menu.setup
end