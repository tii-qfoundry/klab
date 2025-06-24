module KLab
  # This module adds development-specific tools to the KLab menu.
  class DevMenu
    def self.setup
      app = RBA::Application.instance
      mw = app.main_window

      # Find the KLab menu created by the other script.
      menu = mw.menu.find_menu("klab.menu")
      return unless menu # Stop if the main menu doesn't exist

      # Add a separator to visually group the dev tools.
      menu.insert_separator("klab.menu.end", "dev_separator")

      # Create the "Reload KLab Package" action.
      action = RBA::Action.new
      action.title = "Reload KLab Package"
      action.shortcut = "F5" # Assign a convenient shortcut
      
      action.on_triggered do
        # This block executes the Python reload function from dev_tools.py
        pya_script = "from klab.plugin.dev_tools import reload_klab_package; reload_klab_package()"
        RBA::Application.instance.main_window.exec_pya_script(pya_script)
      end
      
      menu.insert_item("klab.menu.end", "reload_klab", action)
    end
  end

  DevMenu.setup
end