@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_positions(request):
    """ Renders all of the positions currently in the chapter """
    # Checking to make sure all of the EC and dashboard required positions are setup
    if request.method == 'POST':
        for position in all_positions:
            if not Position.objects.filter(title=position).exists():
                new_position = Position(title=position)
                new_position.save()
        return HttpResponseRedirect(reverse('dashboard:secretary_positions'))

    positions = Position.objects.order_by("title")
    context = {
        'positions': positions,
    }
    return render(request, "positions.html", context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_position_add(request):
    """ Renders the Secretary way of viewing a brother """
    form = PositionForm(request.POST or None)
    form.fields["title"].choices = [e for e in form.fields["title"].choices if not Position.objects.filter(title=e[0]).exists()]

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('dashboard:secretary_positions'))

    context = {
        'title': 'Add New Position',
        'form': form,
    }
    return render(request, 'model-add.html', context)


class PositionEdit(UpdateView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(PositionEdit, self).get(request, *args, **kwargs)

    model = Position
    success_url = reverse_lazy('dashboard:secretary_positions')
    fields = ['brothers']


class PositionDelete(DeleteView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(PositionDelete, self).get(request, *args, **kwargs)

    model = Position
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:secretary_positions')
