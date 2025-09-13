from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
import io
from PIL import Image

@require_http_methods(["POST"])
def upload_player_avatar(request):
    """Handle player avatar upload with image processing"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        player = Player.objects.get(user=request.user)
    except Player.DoesNotExist:
        return JsonResponse({'error': 'Player profile not found'}, status=404)
    
    if 'avatar' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)
    
    uploaded_file = request.FILES['avatar']
    
    # Validate file type
    if not uploaded_file.content_type.startswith('image/'):
        return JsonResponse({'error': 'File must be an image'}, status=400)
    
    # Validate file size (max 5MB)
    if uploaded_file.size > 5 * 1024 * 1024:
        return JsonResponse({'error': 'File too large. Maximum size is 5MB'}, status=400)
    
    try:
        # Process image
        img = Image.open(uploaded_file)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize and crop to square
        size = 200
        img.thumbnail((size * 2, size * 2), Image.Resampling.LANCZOS)
        
        # Create square crop
        width, height = img.size
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size
        
        img = img.crop((left, top, right, bottom))
        
        # Save processed image
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        # Create new file
        filename = f"avatar_{player.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        processed_file = InMemoryUploadedFile(
            output, 'ImageField', filename, 'image/jpeg',
            output.getbuffer().nbytes, None
        )
        
        # Delete old avatar if exists
        if player.avatar_image:
            player.avatar_image.delete(save=False)
        
        # Save new avatar
        player.avatar_image = processed_file
        player.save()
        
        return JsonResponse({
            'success': True,
            'avatar_url': player.avatar_image.url,
            'message': 'Avatar updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Image processing failed: {str(e)}'}, status=500)

@require_http_methods(["POST"])
def upload_game_screenshot(request):
    """Handle game screenshot upload"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    game_id = request.POST.get('game_id')
    screenshot_type = request.POST.get('type', '1')  # 1, 2, 3, or cover
    
    if not game_id:
        return JsonResponse({'error': 'Game ID required'}, status=400)
    
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    
    if 'screenshot' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)
    
    uploaded_file = request.FILES['screenshot']
    
    try:
        # Process screenshot
        img = Image.open(uploaded_file)
        
        # Convert to RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize for web display
        max_width = 800
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Save processed image
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        # Create filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{game.slug}_{screenshot_type}_{timestamp}.jpg"
        
        processed_file = InMemoryUploadedFile(
            output, 'ImageField', filename, 'image/jpeg',
            output.getbuffer().nbytes, None
        )
        
        # Assign to appropriate field
        field_map = {
            'cover': 'cover_image',
            '1': 'screenshot_1',
            '2': 'screenshot_2',
            '3': 'screenshot_3',
        }
        
        field_name = field_map.get(screenshot_type, 'screenshot_1')
        
        # Delete old image if exists
        old_image = getattr(game, field_name)
        if old_image:
            old_image.delete(save=False)
        
        # Save new image
        setattr(game, field_name, processed_file)
        game.save()
        
        new_image = getattr(game, field_name)
        
        return JsonResponse({
            'success': True,
            'image_url': new_image.url if new_image else None,
            'message': f'Screenshot updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Image processing failed: {str(e)}'}, status=500)

def serve_media_with_permission(request, path):
    """Serve media files with permission checks"""
    # Check if file should be protected
    if path.startswith('players/') and not request.user.is_authenticated:
        return HttpResponse('Authentication required', status=401)
    
    # Serve file using Django's development server (for development only)
    if settings.DEBUG:
        import mimetypes
        from django.http import FileResponse
        
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        
        if os.path.exists(file_path):
            content_type, _ = mimetypes.guess_type(file_path)
            response = FileResponse(
                open(file_path, 'rb'),
                content_type=content_type
            )
            return response
    
    return HttpResponse('File not found', status=404)
