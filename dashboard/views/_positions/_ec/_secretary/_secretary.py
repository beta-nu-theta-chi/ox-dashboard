@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary(request):
    """ Renders the secretary page giving access to excuses and ChapterEvents """
    excuses = Excuse.objects.filter(event__semester=get_semester(), status='0').exclude(event__in=RecruitmentEvent.objects.all()).order_by("date_submitted", "event__date")
    events = ChapterEvent.objects.filter(semester=get_semester()).order_by("start_time").order_by("date")
    brothers = []

    if request.method == 'POST':
        mass_entry_form = BrotherMassEntryForm(request.POST)
        mass_entry_form.fields['brothers'].widget.attrs['readonly'] = False
        is_entry = False

        if "confirmation" in request.POST:
            create_mass_entry_brothers(request, mass_entry_form)
            return HttpResponseRedirect(reverse('dashboard:home'))

        elif "goback" in request.POST:
            is_entry = True  # just want to go back to adding/editting data

        # however else we got here, we need to show the staged data
        else:
            brothers = staged_mass_entry_brothers(mass_entry_form)
    else:
        mass_entry_form = BrotherMassEntryForm()
        is_entry = True

    context = {
        'excuses': excuses,
        'events': events,
        'mass_entry_form': mass_entry_form,
        'is_entry': is_entry, # TODO change to have post stuff
        'brothers': brothers,
    }
    return render(request, 'secretary.html', context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_attendance(request):
    """ Renders the secretary view for chapter attendance """
    brothers = Brother.objects.exclude(brother_status='2').order_by('last_name')
    events = ChapterEvent.objects.filter(semester=get_semester(), mandatory=True)\
        .exclude(date__gt=datetime.date.today())
    excuses = Excuse.objects.filter(event__semester=get_semester(), status='1')
    events_excused_list = []
    events_unexcused_list = []

    for brother in brothers:
        events_excused = 0
        events_unexcused = 0
        for event in events:
            if not event.attendees_brothers.filter(id=brother.id).exists():
                if excuses.filter(brother=brother, event=event).exists():
                    events_excused += 1
                else:
                    events_unexcused += 1
        events_excused_list.append(events_excused)
        events_unexcused_list.append(events_unexcused)

    brother_attendance = zip(brothers, events_excused_list, events_unexcused_list)

    context = {
        'brother_attendance': brother_attendance,
    }

    return render(request, 'chapter-event-attendance.html', context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_event(request, event_id):
    """ Renders the attendance sheet for any event """
    event = Event.objects.get(pk=event_id)
    brothers, brother_form_list = attendance_list(request, event)

    form = EditBrotherAttendanceForm(request.POST or None, event=event_id)

    if request.method == 'POST':
        if "update" in request.POST:
            if forms_is_valid(brother_form_list):
                mark_attendance_list(brother_form_list, brothers, event)
        if "edit" in request.POST:
            if form.is_valid():
                instance = form.cleaned_data
                update_eligible_brothers(instance, event)
        return redirect(request.path_info, kwargs={'event_id': event_id})

    context = {
        'type': 'attendance',
        'brother_form_list': brother_form_list,
        'event': event,
        'form': form,
    }
    return render(request, "chapter-event.html", context)


@verify_position(['Recruitment Chair', 'Secretary', 'Vice President', 'President', 'Adviser'])
def excuse(request, excuse_id):
    """ Renders Excuse response form """
    excuse = get_object_or_404(Excuse, pk=excuse_id)
    form = ExcuseResponseForm(request.POST or None, excuse=excuse)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            excuse.status = instance.status
            excuse.response_message = instance.response_message
            excuse.save()
            return HttpResponseRedirect(request.GET.get('next'))

    context = {
        'type': 'response',
        'excuse': excuse,
        'form': form,
    }
    return render(request, "excuse.html", context)


# accepts the excuse then immediately redirects you back to where you came from
def excuse_quick_accept(request, excuse_id):
    excuse = Excuse.objects.get(pk=excuse_id)
    excuse.status = '1'
    excuse.save()
    return HttpResponseRedirect(request.GET.get('next'))


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_all_excuses(request):
    """ Renders Excuse archive """
    excuses = Excuse.objects.exclude(status='0').exclude(event__in=RecruitmentEvent.objects.all()).order_by('brother__last_name', 'event__date')

    context = {
        'excuses': excuses,
        'position': 'Secretary',
    }
    return render(request, 'excuses_archive.html', context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_event_view(request, event_id):
    """ Renders the Secretary way of viewing old events """
    event = ChapterEvent.objects.get(pk=event_id)
    attendees = event.attendees_brothers.all().order_by("last_name", "first_name")

    context = {
        'type': 'ec-view',
        'attendees': attendees,
        'event': event,
    }
    return render(request, "chapter-event.html", context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_brother_list(request):
    """ Renders the Secretary way of viewing brothers """
    brothers = Brother.objects.exclude(brother_status='2')
    context = {
        'position': 'Secretary',
        'brothers': brothers
    }
    return render(request, "brother-list.html", context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_brother_view(request, brother_id):
    """ Renders the Secretary way of viewing a brother """
    brother = Brother.objects.get(pk=brother_id)
    context = {
        'brother': brother,
        'position': 'Secretary'
    }
    return render(request, "brother-view.html", context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_brother_add(request):
    """ Renders the Secretary way of viewing a brother """
    form = BrotherForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.cleaned_data
            if instance['password'] == instance['password2']:
                user = User.objects.create_user(instance['case_ID'], instance['case_ID'] + "@case.edu",
                                                instance['password'])
                user.last_name = instance['last_name']
                user.save()

                brother = form.save(commit=False)
                brother.user = user
                brother.save()

                return HttpResponseRedirect(reverse('dashboard:secretary_brother_list'))
            else:
                context = {
                    'error_message': "Please make sure your passwords match",
                    'title': 'Add New Brother',
                    'form': form,
                }
                return render(request, 'model-add.html', context)

    context = {
        'title': 'Add New Brother',
        'form': form,
    }
    return render(request, 'model-add.html', context)


class SecretaryBrotherEdit(UpdateView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(SecretaryBrotherEdit, self).get(request, *args, **kwargs)

    model = Brother
    success_url = reverse_lazy('dashboard:secretary_brother_list')
    form_class = BrotherEditForm


class SecretaryBrotherDelete(DeleteView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(SecretaryBrotherDelete, self).get(request, *args, **kwargs)

    model = Brother
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:secretary')


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_event_add(request):
    """ Renders the Secretary way of adding ChapterEvents """
    form = ChapterEventForm(request.POST or None, initial={'name': 'Chapter Event'})

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            save_event(instance)
            return HttpResponseRedirect(reverse('dashboard:secretary'))

    context = {
        'position': 'Secretary',
        'form': form,
    }
    return render(request, "event-add.html", context)


class ChapterEventEdit(UpdateView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(ChapterEventEdit, self).get(request, *args, **kwargs)

    model = ChapterEvent
    success_url = reverse_lazy('dashboard:secretary')
    form_class = ChapterEventForm


class ChapterEventDelete(DeleteView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(ChapterEventDelete, self).get(request, *args, **kwargs)

    model = ChapterEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:secretary')


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_all_events(request):
    """ Renders a secretary view with all the ChapterEvent models ordered by date grouped by semester """
    events_by_semester = []
    semesters = Semester.objects.order_by("season").order_by("year").all()
    for semester in semesters:
        events = ChapterEvent.objects.filter(semester=semester).order_by("date")
        if len(events) == 0:
            events_by_semester.append([])
        else:
            events_by_semester.append(events)
    zip_list = zip(events_by_semester, semesters)
    context = {
        'list': zip_list,
        'position': "Secretary"
    }
    return render(request, "chapter-event-all.html", context)


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


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_agenda(request):
    c_reports = Report.objects.filter(is_officer=False).order_by('brother')
    communications = []
    previous = Brother
    brother = []
    for communication in c_reports:
        if previous == communication.brother:
            brother.append(communication)
        else:
            if brother:
                communications.append(brother)
            brother = [communication]
            previous = communication.brother
    communications.append(brother)

    o_reports = Report.objects.filter(is_officer=True).order_by('position')
    reports = []
    previous = Position
    position = []
    for report in o_reports:
        if previous == report.position:
            position.append(report)
        else:
            if position:
                reports.append(position)
            position = [report]
            previous = report.position
    reports.append(position)

    if request.method == 'POST':
        Report.objects.all().delete()
        return HttpResponseRedirect(reverse('dashboard:secretary_agenda'))

    context = {
        'communications': communications,
        'reports': reports,
    }

    return render(request, 'secretary-agenda.html', context)
