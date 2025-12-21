"""
Copyright (c) 2024 laffra - All Rights Reserved. 

Retrieves and displays a list of sheets in the application's main view.
"""

import constants
import ltk
import state
import menu

import storage

def list_sheets():
    """
    Retrieves and displays a list of sheets in the application's main view.
    """
    state.clear()
    ltk.find("#main").append(
        ltk.Button("New Sheet", ltk.proxy(lambda event: None)).addClass("new-button temporary"),
        ltk.Card(ltk.Div().css("width", 204).css("height", 188)).addClass("document-card temporary"),
        ltk.Card(ltk.Div().css("width", 204).css("height", 188)).addClass("document-card temporary"),
        ltk.Card(ltk.Div().css("width", 204).css("height", 188)).addClass("document-card temporary"),
        ltk.Card(ltk.Div().css("width", 204).css("height", 188)).addClass("document-card temporary"),
        ltk.Card(ltk.Div().css("width", 204).css("height", 188)).addClass("document-card temporary"),
    )
    ltk.find(".temporary").css("opacity", 0).animate(ltk.to_js({ "opacity": 1 }), 2000)
    storage.list_sheets(show_sheet_list)
    ltk.find("#main").animate(ltk.to_js({ "opacity": 1 }), constants.ANIMATION_DURATION)
    ltk.find("#menu").empty().append(menu.create_menu())
    ltk.find("#title").attr("readonly", "true")


def show_sheet_list(sheets):
    """
    Displays a list of sheets in the application's main view. This function is responsible for creating
    the UI elements that represent each sheet, including a screenshot, name, and a click/keyboard
    event handler to load the sheet.
    """
    state.clear()
    ltk.find("#main").empty()

    def delete_sheet(uid, name):
        """Deletes a sheet after user confirmation."""
        def do_delete(event):
            event.stopPropagation()
            
            def confirm_delete(event=None):
                ltk.find("#delete-confirm-modal").remove()
                def on_success(event=None):
                    state.show_message(f"Sheet '{name}' deleted successfully.")
                    storage.list_sheets(show_sheet_list)
                
                def on_error(event=None):
                    show_error_toast(f"Failed to delete sheet '{name}'.")
                
                storage.delete(uid, ltk.proxy(on_success), ltk.proxy(on_error))
            
            def cancel_delete(event=None):
                ltk.find("#delete-confirm-modal").remove()
            
            # Create custom confirmation modal
            modal = ltk.Div(
                ltk.Div(
                    ltk.Div(
                        ltk.Text("🗑️").addClass("confirm-icon"),
                        ltk.Text("Delete Sheet").addClass("confirm-title"),
                        ltk.Text(f"Are you sure you want to delete \"{name}\"?").addClass("confirm-message"),
                        ltk.Text("This action cannot be undone.").addClass("confirm-warning"),
                        ltk.HBox(
                            ltk.Button("Cancel", ltk.proxy(cancel_delete)).addClass("confirm-btn confirm-btn-cancel"),
                            ltk.Button("Delete", ltk.proxy(confirm_delete)).addClass("confirm-btn confirm-btn-delete"),
                        ).addClass("confirm-buttons"),
                    ).addClass("confirm-content")
                ).addClass("confirm-dialog")
            ).attr("id", "delete-confirm-modal").addClass("confirm-modal")
            
            ltk.find("body").append(modal)
            
        return do_delete
    
    def show_error_toast(message):
        """Shows an error toast notification."""
        toast = ltk.Div(
            ltk.Text(message)
        ).addClass("error-toast")
        ltk.find("body").append(toast)
        ltk.schedule(lambda: toast.remove(), "remove-toast", 3)

    def create_card(uid, name, index, runtime, *items):
        def select_doc(event):
            if event.keyCode == 13:
                load_sheet(uid, runtime)

        delete_button = (
            ltk.Button("🗑️", ltk.proxy(delete_sheet(uid, name)))
                .addClass("delete-sheet-button")
                .attr("title", "Delete this sheet")
        )

        return (
            ltk.Card(*items, delete_button)
                .on("click", ltk.proxy(lambda event=None: load_sheet(uid, runtime)))
                .on("keydown", ltk.proxy(select_doc))
                .attr("tabindex", 1000 + index)
                .addClass("document-card")
        )

    ltk.find("#main").append(
        ltk.Container(
            *[
                create_card(
                    sheet.uid,
                    sheet.name,
                    index,
                    "mpy",
                    "",
                    ltk.VBox(
                        ltk.Image(sheet.screenshot),
                        ltk.Text(sheet.name),
                    ),
                )
                for index, sheet in enumerate(sheets)
                if sheet.uid
            ]
        ).prepend(
            ltk.Button("New Sheet", ltk.proxy(lambda event: menu.new_sheet())).addClass(
                "new-button"
            )
        ).css("overflow", "auto").css("height", "100%")
    )
    ltk.find(".document-card").eq(0).focus()
    # state.show_message("Welcome to SheetRL. Select a sheet or create a new one.")


def load_sheet(uid, runtime):
    """
    Loads a sheet.
    
    Args:
        uid (str): The unique identifier of the document to load.
        runtime (str): The runtime environment to use for the document.
    
    Returns:
        None
    """
    url = f"/?{constants.SHEET_ID}={uid}&{constants.PYTHON_RUNTIME}={runtime}"
    ltk.window.location = url
