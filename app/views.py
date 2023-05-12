import sched
import time
from django.http import Http404, HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect
import convertapi
import os
from converter import settings


def delete_file(file_path):
    os.remove(file_path)
    print(f"File {file_path} has been deleted.")


def schedule_file_deletion(file_path, delay_in_minutes):
    s = sched.scheduler(time.time, time.sleep)
    delay_in_seconds = delay_in_minutes * 60
    s.enter(delay_in_seconds, 1, delete_file, argument=(file_path,))
    s.run()


def convert_docx_into_pdf(request):
    convertapi.api_secret = settings.convertapi.api_secret
    if not convertapi.api_secret:
        raise ValueError("CONVERT_API_SECRET is not set in settings.py")
    if request.method == 'POST':
        file_name = request.FILES.get('File')
        formats = ('docx', 'doc', 'dot', 'dotx', 'wpd', 'rtf', 'wri', 'log')
        for format in formats:
            if file_name and file_name.name.endswith(format):
                file_path = os.path.join('media', file_name.name)
                with open(file_path, 'wb+') as f:
                    for chunk in file_name.chunks():
                        f.write(chunk)
                input_file = os.path.join(settings.BASE_DIR, 'media', file_name.name)
                output_dir = os.path.join(settings.BASE_DIR, 'media')
                result = convertapi.convert('pdf', {
                    'File': input_file
                }, from_format='docx').save_files(output_dir)
                pdf_filename = file_name.name.replace(format, 'pdf')
                download_link = reverse('serve_pdf', kwargs={'filename': pdf_filename})
                context = {
                    'api': convertapi.api_secret,
                    'result': result,
                    'download_link': download_link, }
                # schedule_file_deletion(file_path, delay_in_minutes=10)
                return HttpResponse(render(request, 'app/index.html', context))
        return redirect('convert_docx_into_pdf')
    return render(request, 'app/index.html')


def serve_pdf(request, filename):
    try:
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        with open(file_path, 'rb') as f:
            file_content = f.read()
        response = HttpResponse(file_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except FileNotFoundError:
        raise Http404("PDF not found")
