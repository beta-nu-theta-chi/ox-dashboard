from django.views.generic.edit import UpdateView, DeleteView


# a generic class based view used for edit forms for models. Adds the model name to the context under the name 'model'
class DashboardUpdateView(UpdateView):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Adds the model name to the context
        was_last_upper = True
        end_string = ''
        for char in self.model.__name__:
            if char.isupper():
                if not was_last_upper:
                    end_string += ' ' + char
                else:
                    end_string += char
                was_last_upper = True
            else:
                was_last_upper = False
                end_string += char
        context['model'] = end_string
        return context


# this is a placeholder to make global changes to the delete view easier
class DashboardDeleteView(DeleteView):
    pass
