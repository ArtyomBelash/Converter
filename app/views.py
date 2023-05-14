from django.http import Http404, HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect
import convertapi
import os
from converter import settings


def convert_docx_into_pdf(request):
    convertapi.api_secret = settings.convertapi.api_secret
    if not convertapi.api_secret:
        raise ValueError("CONVERT_API_SECRET is not set in settings.py")
    if request.method == 'POST':
        file_name = request.FILES.get('File')
        formats = ('docx', 'doc', 'dot', 'dotx', 'wpd', 'rtf', 'wri', 'log')
        for i in formats:
            if file_name and file_name.name.endswith(i):
                file_path = os.path.join('media', file_name.name)
                with open(file_path, 'wb+') as f:
                    for chunk in file_name.chunks():
                        f.write(chunk)
                input_file = os.path.join(settings.BASE_DIR, 'media', file_name.name)
                output_dir = os.path.join(settings.BASE_DIR, 'media')
                result = convertapi.convert('pdf', {
                    'File': input_file
                }, from_format='docx').save_files(output_dir)
                pdf_filename = file_name.name.replace(i, 'pdf')
                download_link = reverse('serve_pdf', kwargs={'filename': pdf_filename})
                context = {
                    'api': convertapi.api_secret,
                    'result': result,
                    'download_link': download_link, }
                return HttpResponse(render(request, 'app/index.html', context))
        return redirect('convert_docx_into_pdf')
    files_path = os.path.join(settings.BASE_DIR, 'media')
    files = os.listdir(files_path)
    for file in files:
        file_path = os.path.join(files_path, file)
        os.remove(file_path)
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
