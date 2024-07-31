from functools import partial
import random
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.app import App
from kivy.uix.togglebutton import ToggleButton

Default_Tasks = {
    "Doorkeeper in": 1, "Doorkeeper out": 1, "Usher out": 1, "Usher staff": 2, "Usher participants": 2,
    "Floater": 2, "Registration": 3, "Craft distributor": 2, "Welcoming": 2, 'Timekeeper': 1
}
Tasks = {
    "Doorkeeper in": 1, "Doorkeeper out": 1, "Usher out": 1, "Usher staff": 2, "Usher participants": 2,
    "Floater": 2, "Registration": 3, "Craft distributor": 2, "Welcoming": 2, 'Timekeeper': 1
}
Names = {
    "Abed": 1, "Asmaa": 1, "Basmala": 1, "Batol Ali": 1, "Batol Osama": 1, "Hana": 1, "Hana (Fnoon)": 1, "Israa": 1,
    "Mai": 1, "Malak": 1, "Menna": 1, "Milo": 1, "Mohamed": 1, "Moustafa": 1, "Nada": 1, "Nayera": 1, "Omar": 1,
    "Rahma": 1, "Sama": 1, "Sara": 1, "Sara Atef": 1, "Shadia": 1, "Shahd (STEM)": 1, "Shahd": 1, "Shrouk": 1,
    "Toka": 1, "Youseff": 1
}
Attended = []
Staff_Assigned = False
First_Shift = {}
Current_Shift = {}
Next_Shift = {}
Previous_Shift = ''
Previous_Tasks = {}
formatted_text = ''


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.spacing = 3
        b1 = ScalableButton(text='Current Shift')
        b2 = ScalableButton(text='Next Shift')
        b3 = ScalableButton(text='Previous Shift')
        b4 = ScalableButton(text='Staff')
        b5 = ScalableButton(text='Tasks')

        b1.bind(on_press=lambda instance: self.check_attended(b1.text))
        b2.bind(on_press=lambda instance: self.check_attended(b2.text))
        b3.bind(on_press=lambda instance: self.check_attended(b3.text))
        b4.bind(on_press=self.go_to_staff_screen)
        b5.bind(on_press=lambda instance: self.check_attended(b5.text))

        layout.add_widget(b1)
        layout.add_widget(b2)
        layout.add_widget(b3)
        layout.add_widget(b4)
        layout.add_widget(b5)
        self.add_widget(layout)

    def check_attended(self, name):
        global Staff_Assigned
        if Attended:
            if name == 'Current Shift':
                self.go_to_current_screen(name)
            elif name == 'Next Shift':
                if First_Shift:
                    self.go_to_next_screen(name)
                else:
                    self.show_popup('First shift not assigned!', "First shift hasn't been assigned yet.")
            elif name == 'Previous Shift':
                if Previous_Shift:
                    self.go_to_previous_screen(name)
                else:
                    self.show_popup('No previous shift', 'There is currently no previous shift.')
            else:
                self.go_to_tasks_screen(name)
        else:
            self.show_popup('Staff attendance not recorded', 'Please record staff attendance before proceeding.')

    def go_to_current_screen(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'current_screen'

    def go_to_next_screen(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'next_screen'

    def go_to_previous_screen(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'previous_screen'

    def go_to_staff_screen(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'staff_screen'

    def go_to_tasks_screen(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'tasks_screen'

    def show_popup(self, title, message):
        content = ResponsiveLabel(text=message)
        popup = Popup(title=title,
                      content=content,
                      size_hint=(.65, .65))
        popup.open()


class CurrentScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.label = ResponsiveLabel(text='Current Shift')
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, .2))
        b1 = ScalableButton(text='Back to main menu', size_hint=(.5, 1), size=("400dp", "400dp"))
        b2 = ScalableButton(text='Assign first shift', size_hint=(.5, 1), size=("400dp", "400dp"))
        b3 = ScalableButton(text='Edit', size_hint=(1, .2))

        b1.bind(on_press=self.go_back_to_main_menu)
        b2.bind(on_press=self.go_to_first_shift)
        b3.bind(on_press=self.go_to_edit_screen)

        button_layout.add_widget(b1)
        button_layout.add_widget(b2)
        layout.add_widget(button_layout)
        layout.add_widget(b3)
        layout.add_widget(self.label)

        self.add_widget(layout)

    def update_current_shift(self):
        self.label.text = formatted_text

    def on_shift_changed(self):
        self.update_current_shift()

    def on_enter(self, *args):
        Window.bind(on_keyboard=self.back_btn)

    def on_leave(self, *args):
        Window.unbind(on_keyboard=self.back_btn)

    def back_btn(self, window, key, *args):
        if key == 27:
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'main_screen'
            return True

    def show_popup(self, title, message):
        content = ResponsiveLabel(text=message)
        popup = Popup(title=title,
                      content=content,
                      size_hint=(.65, .65))
        popup.open()

    def go_back_to_main_menu(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main_screen'

    def go_to_edit_screen(self, instance):
        if Current_Shift:
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'edit_screen'
        else:
            self.show_popup('No shift currently', 'There is currently no shift.')
    def go_to_first_shift(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'first_shift_screen'


class FirstShiftScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.buttons = {}
        self.layout = BoxLayout(orientation='vertical')
        self.button_layout = BoxLayout(orientation='horizontal', size_hint=(1, .18))

        self.b1 = ScalableButton(text='Back to Current Shift menu', size_hint=(.33, 1), size=("400dp", "400dp"))
        self.b2 = ScalableButton(text='Finish assigning', size_hint=(.33, 1), size=("400dp", "400dp"))
        self.b3 = ScalableButton(text='Reset', size_hint=(.33, 1), size=("400dp", "400dp"))

        self.b1.bind(on_press=self.go_back_to_current_screen)
        self.b2.bind(on_press=self.check_first_shift)
        self.b3.bind(on_press=self.reset_first_shift)

        self.button_layout.add_widget(self.b1)
        self.button_layout.add_widget(self.b2)
        self.button_layout.add_widget(self.b3)
        self.layout.add_widget(self.button_layout)

        self.add_widget(self.layout)

    def update_task_layout(self):
        # Clear existing task layouts if needed
        self.layout.clear_widgets()
        self.layout.add_widget(self.button_layout)

        for task in Tasks.keys():
            task_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', padding=0, spacing=0)
            l1 = ScalableButton(text=task, size_hint=(.33, 1), background_color=(.64, .62, .62, 1))
            l2 = ScalableButton(text='Number of staff: ' + f'{Tasks[task]}', size_hint=(.33, 1), background_color=(.64, .62, .62, 1))
            button = MultiSelectDropdown(text="Names", values=Attended, size_hint=(.33, 1), background_color=(.64, .62, .62, 1))
            self.buttons[task] = button

            task_layout.add_widget(l1)
            task_layout.add_widget(l2)
            task_layout.add_widget(button)
            self.layout.add_widget(task_layout)

    def check_first_shift(self, instance):
        global First_Shift
        if First_Shift:
            self.show_popup('First shift already assigned', 'Please reset first shift first.')
        else:
            self.finish_first_shift(instance)

    def on_attended_changed(self):
        self.update_task_layout()

    def on_enter(self, *args):
        Window.bind(on_keyboard=self.back_btn)

    def on_leave(self, *args):
        Window.unbind(on_keyboard=self.back_btn)

    def back_btn(self, window, key, *args):
        if key == 27:
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'current_screen'  # Change this to current_screen
            return True

    def go_back_to_current_screen(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'current_screen'

    def finish_first_shift(self, instance):
        global First_Shift, Tasks, Current_Shift, Previous_Tasks
        error_shown = False  # Flag to track if an error message has been shown
        for task in Tasks.keys():
            if Tasks[task] == len(self.buttons[task].selected_values) or task == 'Timekeeper':
                for name in self.buttons[task].selected_values:
                    if name in First_Shift.keys():
                        self.reset_first_shift(instance)
                        self.show_popup('error: One or more staff members assigned to multiple tasks!',
                                        'One or more staff members assigned to\nmultiple tasks, please assign staff accordingly.')
                        error_shown = True
                        break
                    else:
                        First_Shift[name] = task
                        Previous_Tasks[name][0] += 1
                        Previous_Tasks[name][1] = task
                if error_shown:
                    break
            else:
                self.reset_first_shift(instance)
                self.show_popup('error: Number of names fewer or more than required!',
                                'Number of names fewer or more than\nrequired staff, please assign staff accordingly.')
                error_shown = True
                break

        if not error_shown and First_Shift:
            self.show_popup('First shift assigned!', 'First shift has been assigned and copied to clipboard.')
            self.copy_shift(instance)
            Current_Shift = First_Shift

            screen_manager = App.get_running_app().root
            screen_instance = screen_manager.get_screen('current_screen')
            screen_instance.on_shift_changed()

            screen_instance = screen_manager.get_screen('edit_screen')
            screen_instance.on_current_shift_changed()

        print(First_Shift)
        print(Current_Shift)
        print(Previous_Tasks)

    def reset_first_shift(self, instance):
        global First_Shift, formatted_text
        First_Shift = {}
        for task in Tasks.keys():
            self.buttons[task].selected_values = []
            self.buttons[task].update_button_text()
        self.show_popup('First Shift Reset!', 'Please reassign first shift.')
        screen_manager = App.get_running_app().root
        screen_instance = screen_manager.get_screen('current_screen')
        screen_instance.on_shift_changed()
        formatted_text = ''
        print(First_Shift)

    def copy_shift(self, instance):
        global First_Shift, formatted_text
        task_to_names = {}

        for name, task in First_Shift.items():
            if task not in task_to_names:
                task_to_names[task] = []
            task_to_names[task].append(name)

        formatted_output = []
        for task, names in task_to_names.items():
            if len(names) > 1:
                formatted_output.append(f"{task}: {', '.join(names)}")
            else:
                formatted_output.append(f"{task}: {names[0]}")

        formatted_text = '\n'.join(formatted_output)
        Clipboard.copy(formatted_text)
        print(formatted_text)

    def show_popup(self, title, message):
        content = ResponsiveLabel(text=message)
        popup = Popup(title=title,
                      content=content,
                      size_hint=(.65, .65))
        popup.open()


class EditScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.buttons = {}
        self.layout = BoxLayout(orientation='vertical')
        self.button_layout = BoxLayout(orientation='horizontal', size_hint=(1, .18))

        self.b1 = ScalableButton(text='Back to Current Shift menu', size_hint=(.33, 1), size=("400dp", "400dp"))
        self.b2 = ScalableButton(text='Finish assigning', size_hint=(.33, 1), size=("400dp", "400dp"))

        self.b1.bind(on_press=self.go_back_to_current_screen)
        self.b2.bind(on_press=self.finish_editing)

        self.button_layout.add_widget(self.b1)
        self.button_layout.add_widget(self.b2)
        self.layout.add_widget(self.button_layout)
        self.add_widget(self.layout)

    def update_task_layout(self):
        # Clear existing task layouts if needed
        self.layout.clear_widgets()
        self.layout.add_widget(self.button_layout)

        # Reverse mapping of Current_Shift to get task to names mapping
        task_to_names = {}
        for name, task in Current_Shift.items():
            if task not in task_to_names:
                task_to_names[task] = []
            task_to_names[task].append(name)

        for task in Tasks.keys():
            task_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', padding=0, spacing=0)
            l1 = ScalableButton(text=task, size_hint=(.33, 1), background_color=(.64, .62, .62, 1))
            l2 = ScalableButton(text='Number of staff: ' + f'{Tasks[task]}', size_hint=(.33, 1), background_color=(.64, .62, .62, 1))
            selected_values = task_to_names.get(task, [])
            button = MultiSelectDropdown(text="Names", values=Attended, selected_values=selected_values, size_hint=(.33, 1), background_color=(.64, .62, .62, 1))
            button.text = ', '.join(selected_values) if selected_values else 'Names'
            self.buttons[task] = button

            task_layout.add_widget(l1)
            task_layout.add_widget(l2)
            task_layout.add_widget(button)
            self.layout.add_widget(task_layout)

    def finish_editing(self, instance):
        global First_Shift, Tasks, Current_Shift, Previous_Tasks
        updated_current_shift = {}
        error_shown = False  # Flag to track if an error message has been shown
        for task in Tasks.keys():
            if Tasks[task] == len(self.buttons[task].selected_values) or task == 'Timekeeper':
                for name in self.buttons[task].selected_values:
                    if name in updated_current_shift.keys():
                        self.show_popup('error: One or more staff members assigned to multiple tasks!',
                                        'One or more staff members assigned to\nmultiple tasks, please assign staff accordingly.')
                        error_shown = True
                        break
                    else:
                        if name not in Current_Shift.keys():
                            Previous_Tasks[name][0] += 1
                        if Previous_Tasks[name][1] != task:
                            Previous_Tasks[name][1] = task
                        updated_current_shift[name] = task
                if error_shown:
                    break
            else:
                self.show_popup('error: Number of names fewer or more than required!',
                                'Number of names fewer or more than\nrequired staff, please assign staff accordingly.')
                error_shown = True
                break

        if not error_shown and First_Shift:
            self.show_popup('Current shift changed!', 'Current shift has been edited and copied to clipboard.')
            Current_Shift = updated_current_shift
            self.copy_shift(instance)

            screen_manager = App.get_running_app().root
            screen_instance = screen_manager.get_screen('current_screen')
            screen_instance.on_shift_changed()

        print(Current_Shift)
        print(Previous_Tasks)

    def copy_shift(self, instance):
        global Current_Shift, formatted_text
        task_to_names = {}

        for name, task in Current_Shift.items():
            if task not in task_to_names:
                task_to_names[task] = []
            task_to_names[task].append(name)

        formatted_output = []
        for task, names in task_to_names.items():
            if len(names) > 1:
                formatted_output.append(f"{task}: {', '.join(names)}")
            else:
                formatted_output.append(f"{task}: {names[0]}")

        formatted_text = '\n'.join(formatted_output)
        Clipboard.copy(formatted_text)
        print(formatted_text)

    def show_popup(self, title, message):
        content = ResponsiveLabel(text=message)
        popup = Popup(title=title,
                      content=content,
                      size_hint=(.65, .65))
        popup.open()

    def on_current_shift_changed(self):
        self.update_task_layout()

    def on_enter(self, *args):
        Window.bind(on_keyboard=self.back_btn)

    def on_leave(self, *args):
        Window.unbind(on_keyboard=self.back_btn)

    def back_btn(self, window, key, *args):
        if key == 27:
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'current_screen'  # Change this to current_screen
            return True

    def go_back_to_current_screen(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'current_screen'


class NextScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, .2))
        self.label = ResponsiveLabel(text='Next Shift')
        b1 = ScalableButton(text='Back to main menu')
        b2 = ScalableButton(text='Generate shift')
        b3 = ScalableButton(text='Set as current shift', size_hint=(1, .2))

        b1.bind(on_press=self.go_back_to_main_menu)
        b2.bind(on_press=self.generate_shift)
        b3.bind(on_press=self.show_confirmation_popup)

        button_layout.add_widget(b1)
        button_layout.add_widget(b2)
        layout.add_widget(button_layout)
        layout.add_widget(b3)
        layout.add_widget(self.label)
        self.add_widget(layout)

    def on_enter(self, *args):
        Window.bind(on_keyboard=self.back_btn)

    def on_leave(self, *args):
        Window.unbind(on_keyboard=self.back_btn)

    def back_btn(self, window, key, *args):
        if key == 27:
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'main_screen'
            return True

    def go_back_to_main_menu(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main_screen'

    def generate_shift(self, instance):
        global Next_Shift, Previous_Shift

        # Find the minimum workload
        min_workload = min(val[0] for val in Previous_Tasks.values())

        # Get the staff with the minimum workload
        available_staff = [name for name, val in Previous_Tasks.items() if val[0] == min_workload]

        # Filter out staff who worked the last shift if everyone has the same number of tasks worked
        if len(available_staff) == len(Previous_Tasks):
            available_staff = [name for name in available_staff if name not in Previous_Shift]

        # Filter out the "Timekeeper" task and adjust the tasks for required staff count
        assignable_tasks = {task: count for task, count in Tasks.items() if task != 'Timekeeper'}

        # Create a list to hold the new assignments
        new_assignments = {}

        # Ensure we can still assign tasks even if there are not enough staff with the minimum workload
        for task, count in assignable_tasks.items():
            while count > 0:
                if not available_staff:
                    # Refresh the available staff list with the next minimum workload
                    min_workload += 1
                    available_staff = [name for name, val in Previous_Tasks.items() if val[0] == min_workload]
                    if not available_staff:
                        break

                staff_member = random.choice(available_staff)
                while Previous_Tasks[staff_member][1] == task:
                    available_staff.remove(staff_member)
                    if not available_staff:
                        # Refresh the available staff list with the next minimum workload
                        min_workload += 1
                        available_staff = [name for name, val in Previous_Tasks.items() if val[0] == min_workload]
                        if not available_staff:
                            break
                    staff_member = random.choice(available_staff)

                if not available_staff:
                    break

                new_assignments[staff_member] = task
                available_staff.remove(staff_member)
                count -= 1

        # Retain the Timekeeper if it was previously assigned
        for name, val in Previous_Tasks.items():
            if val[1] == 'Timekeeper':
                new_assignments[name] = 'Timekeeper'
                break

        Next_Shift = new_assignments
        Previous_Shift = formatted_text
        self.format_shift_text(instance)
        self.label.text = formatted_text

    def change_current_shift(self, instance):
        global Current_Shift, Next_Shift
        if Next_Shift:
            Clipboard.copy(self.label.text)
            Current_Shift = Next_Shift
            for name in Next_Shift.keys():
                Previous_Tasks[name][0] += 1
                Previous_Tasks[name][1] = Next_Shift[name]

            screen_manager = App.get_running_app().root
            screen_instance = screen_manager.get_screen('current_screen')
            screen_instance.on_shift_changed()

            screen_instance = screen_manager.get_screen('edit_screen')
            screen_instance.on_current_shift_changed()

            screen_instance = screen_manager.get_screen('previous_screen')
            screen_instance.on_shift_changed()

            self.label.text = 'Next Shift'
            Next_Shift = {}
            print(formatted_text)
            print(Current_Shift)
            print(Previous_Tasks)
        else:
            self.show_popup('No new shift generated', 'Please generate a new shift first.')

    def format_shift_text(self, instance):
        global Next_Shift, formatted_text
        task_to_names = {}

        for name, task in Next_Shift.items():
            if task not in task_to_names:
                task_to_names[task] = []
            task_to_names[task].append(name)

        formatted_output = []
        for task, names in task_to_names.items():
            if len(names) > 1:
                formatted_output.append(f"{task}: {', '.join(names)}")
            else:
                formatted_output.append(f"{task}: {names[0]}")

        formatted_text = '\n'.join(formatted_output)

    def show_confirmation_popup(self, instance):
        title = 'Are you sure?'
        message = 'This will replace the current shift with the next shift.'

        # Define the content layout for the popup
        content = BoxLayout(orientation='vertical')
        message_label = Label(text=message)
        button_layout = BoxLayout(size_hint_y=None, height='40dp', spacing='5dp')

        # Define the buttons
        confirm_button = Button(text='Confirm')
        cancel_button = Button(text='Cancel')

        # Create the popup
        popup = Popup(title=title, content=content, size_hint=(.75, .5))

        # Bind buttons after popup creation so `popup.dismiss` works correctly
        confirm_button.bind(on_press=self.change_current_shift)
        confirm_button.bind(on_press=lambda *args: popup.dismiss())
        cancel_button.bind(on_press=lambda *args: popup.dismiss())

        # Add buttons to the button layout
        button_layout.add_widget(cancel_button)
        button_layout.add_widget(confirm_button)

        # Add widgets to the content layout
        content.add_widget(message_label)
        content.add_widget(button_layout)

        popup.open()

    def show_popup(self, title, message):
        content = ResponsiveLabel(text=message)
        popup = Popup(title=title,
                      content=content,
                      size_hint=(.65, .65))
        popup.open()


class PreviousScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.label = ResponsiveLabel(text='Previous Shift')
        b1 = ScalableButton(text='Back to main menu', size_hint=(1, .2))
        b1.bind(on_press=self.go_back_to_main_menu)

        layout.add_widget(b1)
        layout.add_widget(self.label)
        self.add_widget(layout)

    def on_enter(self, *args):
        Window.bind(on_keyboard=self.back_btn)

    def on_leave(self, *args):
        Window.unbind(on_keyboard=self.back_btn)

    def back_btn(self, window, key, *args):
        if key == 27:
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'main_screen'
            return True

    def go_back_to_main_menu(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main_screen'

    def on_shift_changed(self):
        self.update_previous_shift()

    def update_previous_shift(self):
        self.label.text = Previous_Shift


class StaffScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.buttons = {}
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, .15))
        name_layout = GridLayout(cols=3, rows=10)
        main_layout = BoxLayout(orientation='vertical')
        b1 = ScalableButton(text='Back to main menu')
        b1.bind(on_press=self.go_back_to_main_menu)
        b2 = ScalableButton(text='Finish Attendance')
        b2.bind(on_press=self.check_attended)
        b3 = ScalableButton(text='Edit')
        b3.bind(on_press=self.edit_attendance)
        b4 = ScalableButton(text='Reset')
        b4.bind(on_press=self.reset_attendance)

        button_layout.add_widget(b1)
        button_layout.add_widget(b2)
        button_layout.add_widget(b3)
        button_layout.add_widget(b4)

        self.green_color = (0, 1, 0, 1)  # RGBA for green
        self.red_color = (1, 0, 0, 1)  # RGBA for red

        for name in (Names.keys()):
            button = Button(text=name, background_color=self.green_color)
            button.bind(on_press=self.change_attendance)
            self.buttons[name] = button
            name_layout.add_widget(button)
        main_layout.add_widget(button_layout)
        main_layout.add_widget(name_layout)
        self.add_widget(main_layout)

    def on_enter(self, *args):
        Window.bind(on_keyboard=self.back_btn)

    def on_leave(self, *args):
        Window.unbind(on_keyboard=self.back_btn)

    def check_attended(self, instance):
        if not Staff_Assigned:
            self.finish_attendance(instance)
        else:
            self.show_popup('Staff attendance already recorded', 'Please reset or edit first before trying\nto record staff again.')

    def change_attendance(self, button):
        current_color = tuple(button.background_color)  # Convert to tuple for comparison
        if Staff_Assigned:
            self.show_popup('Staff attendance already recorded', 'Please reset or edit first before trying\nto record staff again.')
        else:
            if current_color == self.green_color:
                button.background_color = self.red_color
                Names[button.text] = 0
            else:
                button.background_color = self.green_color
                Names[button.text] = 1

    def finish_attendance(self, instance):
        global Attended, Staff_Assigned, Previous_Tasks
        attendees = [key for key, value in Names.items() if value == 1]
        Attended = attendees
        Staff_Assigned = True

        for name in Attended:
            if name not in Previous_Tasks.keys():
                Previous_Tasks[name] = [0, None]
        for name, button in self.buttons.items():
            if tuple(button.background_color) == self.red_color and name in Previous_Tasks.keys():
                del Previous_Tasks[name]

        self.show_popup('Attendance has been saved!', 'Please head to "Current Shift" and assign the first shift.')
        if len(Attended) < 17:
            self.show_popup('Warning: Attended staff fewer than default number', 'Attended staff fewer than default number of\n'
                                                                                'staff required for tasks, please head to "tasks" screen\n'
                                                                                'and assign task numbers accordingly.')

        screen_manager = App.get_running_app().root
        screen_instance = screen_manager.get_screen('first_shift_screen')
        screen_instance.on_attended_changed()

        print(Attended)
        print(Previous_Tasks)

    def edit_attendance(self, instance):
        global Attended, Previous_Tasks, Staff_Assigned, Names
        Staff_Assigned = False

        for name, button in self.buttons.items():
            if tuple(button.background_color) == self.green_color:
                Names[name] = 1
                if name not in Attended:
                    Previous_Tasks[name] = [0, None]
            else:
                Names[name] = 0

        self.show_popup('Please edit attendance!', 'Please edit attendance then click "Finish Attendance".')

    def reset_attendance(self, instance):
        global Attended, Staff_Assigned, Previous_Tasks, Names
        if not First_Shift:
            for name in Names.keys():
                self.buttons[name].background_color = self.green_color
                Names[name] = 1
            Attended = None
            Previous_Tasks = {}
            Staff_Assigned = False
            self.show_popup('Attendance has been reset', 'Please record the attendance.')
            print(Attended)
        else:
            self.show_popup('First shift was assigned', 'Cannot reset after first shift was assigned')

    def show_popup(self, title, message):
        content = ResponsiveLabel(text=message)
        popup = Popup(title=title,
                      content=content,
                      size_hint=(.65, .65))
        popup.open()

    def back_btn(self, window, key, *args):
        if key == 27:
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'main_screen'
            return True

    def go_back_to_main_menu(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main_screen'


class TasksScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.buttons = {}
        top_layout = BoxLayout(orientation='horizontal', size_hint=(1, .2))
        main_layout = BoxLayout(orientation='vertical')
        b1 = ScalableButton(text='Back to main menu')
        b2 = ScalableButton(text='Finish')
        b3 = ScalableButton(text='Reset to default')

        b1.bind(on_press=self.go_back_to_main_menu)
        b2.bind(on_press=self.finish_tasks)
        b3.bind(on_press=self.reset_tasks)

        top_layout.add_widget(b1)
        top_layout.add_widget(b2)
        top_layout.add_widget(b3)
        main_layout.add_widget(top_layout)

        for task in Default_Tasks.keys():
            task_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', padding=0, spacing=0)
            label = ScalableButton(text=task, size_hint=(.5, 1), background_color=(.64, .62, .62, 1))
            button = Button(text=f'{Default_Tasks[task]}', size_hint=(.5, 1), background_color=(.64, .62, .62, 1))

            dropdown = DropDown()
            for i in range(0, 5):
                btn = Button(text=f'{i}', size_hint_y=None, height=44)
                btn.bind(on_release=partial(self.select_dropdown, dropdown, btn, button))
                dropdown.add_widget(btn)

            button.bind(on_release=self.create_open_dropdown(dropdown))

            self.buttons[task] = button
            task_layout.add_widget(label)
            task_layout.add_widget(button)
            main_layout.add_widget(task_layout)

        self.add_widget(main_layout)

    def create_open_dropdown(self, dropdown):
        def open_dropdown(button_instance):
            dropdown.open(button_instance)

        return open_dropdown

    def select_dropdown(self, dropdown, dropdown_btn, button, *args):
        dropdown.select(dropdown_btn.text)
        button.text = dropdown_btn.text

    def finish_tasks(self, instance):
        global Tasks, Default_Tasks, Attended
        total_tasks = 0
        total_staff = len(Attended)
        for task in Default_Tasks.keys():
            Tasks[task] = int(self.buttons[task].text)
        for task_num in Tasks.values():
            total_tasks += task_num
        if total_tasks > total_staff:
            self.reset_tasks(instance)
            self.show_popup('error: Fewer staff than tasks', 'Attended staff fewer than set tasks.')
        else:
            screen_manager = App.get_running_app().root
            screen_instance = screen_manager.get_screen('first_shift_screen')
            screen_instance.on_attended_changed()
            self.show_popup("Tasks have been saved!", "Tasks' staff numbers have been set.")
        print(Tasks)

    def reset_tasks(self, instance):
        global Tasks, Default_Tasks
        for task in Default_Tasks.keys():
            Tasks[task] = Default_Tasks[task]
            self.buttons[task].text = str(Default_Tasks[task])
        screen_manager = App.get_running_app().root
        screen_instance = screen_manager.get_screen('first_shift_screen')
        screen_instance.on_attended_changed()
        self.show_popup('Tasks has been reset', 'Tasks have been reset to default.')
        print(Tasks)

    def go_back_to_main_menu(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'main_screen'

    def on_enter(self, *args):
        Window.bind(on_keyboard=self.back_btn)

    def on_leave(self, *args):
        Window.unbind(on_keyboard=self.back_btn)

    def back_btn(self, window, key, *args):
        if key == 27:
            self.manager.transition = SlideTransition(direction='right')
            self.manager.current = 'main_screen'
            return True

    def show_popup(self, title, message):
        content = ResponsiveLabel(text=message)
        popup = Popup(title=title,
                      content=content,
                      size_hint=(.65, .65))
        popup.open()


class ResponsiveLabel(Label):
    font_size = NumericProperty(20)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(size=self.update_font_size)

    def update_font_size(self, *args):
        self.font_size = Window.width / 40  # Adjust this divisor to get the desired font size


class ScalableButton(Button):
    font_size = NumericProperty(20)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(size=self.update_font_size)

    def update_font_size(self, *args):
        self.font_size = Window.width / 36  # Adjust this divisor to get the desired font size


class MultiSelectDropdown(Button):
    """Widget allowing to select multiple text options."""

    dropdown = ObjectProperty(None)
    """(internal) DropDown used with MultiSelectDropdown."""

    values = ListProperty([])
    """Values to choose from."""

    selected_values = ListProperty([])
    """List of values selected by the user."""

    def __init__(self, **kwargs):
        super(MultiSelectDropdown, self).__init__(**kwargs)
        self.bind(on_release=self.toggle_dropdown)
        self.dropdown = DropDown()
        Window.bind(size=self.update_font_size)

    def toggle_dropdown(self, *args):
        if self.dropdown.parent:
            self.dropdown.dismiss()
        else:
            self.update_dropdown()
            self.dropdown.open(self)

    def update_dropdown(self, *args):
        self.dropdown.clear_widgets()
        for value in self.values:
            btn = ToggleButton(text=value, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.select_value(btn))
            if btn.text in self.selected_values:
                btn.state = 'down'
            self.dropdown.add_widget(btn)

    def select_value(self, btn):
        if btn.state == 'down':
            if btn.text not in self.selected_values:
                self.selected_values.append(btn.text)
        else:
            if btn.text in self.selected_values:
                self.selected_values.remove(btn.text)
        self.update_button_text()

    def update_button_text(self):
        if self.selected_values:
            self.text = ', '.join(self.selected_values)
        else:
            self.text = 'Select options'

    def update_font_size(self, *args):
        self.font_size = Window.width / 40  # Adjust this divisor to get the desired font size


class TaskWizardApp(App):
    def build(self):
        # Create the ScreenManager
        sm = ScreenManager()

        # Add the screens to the manager
        sm.add_widget(MainScreen(name='main_screen'))
        sm.add_widget(CurrentScreen(name='current_screen'))
        sm.add_widget(FirstShiftScreen(name='first_shift_screen'))
        sm.add_widget(EditScreen(name='edit_screen'))
        sm.add_widget(NextScreen(name='next_screen'))
        sm.add_widget(PreviousScreen(name='previous_screen'))
        sm.add_widget(StaffScreen(name='staff_screen'))
        sm.add_widget(TasksScreen(name='tasks_screen'))

        return sm


TaskWizardApp().run()
