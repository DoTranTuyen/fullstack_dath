import os
from web_01.models import Product, Category, Ingredient, IngredientProduct
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import cloudinary.uploader
from io import BytesIO
import requests
import pandas as pd
from core.__Include_Library import *
from django.shortcuts import render
from django.views.generic import TemplateView
import json
from web_01.models import Product, IngredientProduct, Ingredient, OrderDetail
from django.forms import inlineformset_factory
from django.db.models import Sum


class ProductManagementView(LoginRequiredMixin, TemplateView):
    template_name = 'apps/web_01/product/product_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_list'] = Category.objects.filter(status='active').values_list('id', 'name')
        context['price_list'] = [
            ('10000-50000', '10.000đ - 50.000đ'),
            ('50000-100000', '50.000đ - 100.000đ'),
            ('100000-150000', '100.000đ - 150.000đ'),
            ('150000-200000', '150.000đ - 200.000đ'),
            ('200000-1000000', 'Trên 200.000đ'),
        ]
        return context

    def post(self, request, *args, **kwargs):
        try:
            draw = int(request.POST.get("draw", 1))
            start = int(request.POST.get("start", 0))
            length = int(request.POST.get("length", 10))
            search_value = request.POST.get("search[value]", "").strip()
            # Lấy dữ liệu từ request
            category = request.POST.get("category", "[]")  # Nếu không có, mặc định là []
            price = request.POST.get("price", "-1")
            category_ids = json.loads(category)  # Chuyển từ JSON thành danh sách Python

            order_column_index = int(request.POST.get("order[0][column]", 0))
            order_dir = request.POST.get("order[0][dir]", "asc")

            column_mapping = {
                0: "id",
                1: "name",
                2: "image",
                3: "category__name",
                4: "price"
            }

            # Kiểm tra nếu index không hợp lệ
            if order_column_index not in column_mapping:
                order_column_index = 0

            order_column = column_mapping[order_column_index]

            # Sắp xếp theo thứ tự ASC/DESC
            if order_dir == "desc":
                order_column = "-" + order_column

            # Query sản phẩm từ database
            product_list = Product.objects.select_related("category")

            filter_dict = dict()
            if category_ids:
                filter_dict['category_id__in'] = category_ids

            if search_value:
                filter_dict['name__icontains'] = search_value

            if price != "-1":
                min_price, max_price = price.split('-')
                filter_dict['price__gte'] = int(min_price)
                filter_dict['price__lte'] = int(max_price)

            product_list = product_list.filter(**filter_dict).order_by(order_column)
            total_count = product_list.count()
            product_list = product_list[start: start + length]  # Sort + Pagination

            # Chuẩn bị dữ liệu JSON
            products_data = [
                {
                    "index": index + 1,
                    "id": product.id,
                    "name": product.name,
                    "image": product.image.url if product.image else None,
                    "status": product.status,
                    "category": product.category.name if product.category else "Không có danh mục",
                    "price": f"{product.price:,} VND",
                }
                for index, product in enumerate(product_list, start=start)
            ]

            return JsonResponse({
                "draw": draw,
                "recordsTotal": total_count,
                "recordsFiltered": total_count,
                "data": products_data
            }, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

class ExportProductsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Lấy tham số từ URL
        category_ids = request.GET.get('category', '')
        price_range = request.GET.get('price', '-1')
        status = request.GET.get('status', 'all')
        
        # Xây dựng query
        query = Product.objects.select_related('category')
        
        # Áp dụng bộ lọc
        if category_ids:
            category_list = [int(cat_id) for cat_id in category_ids.split(',')]
            query = query.filter(category_id__in=category_list)
            
        if price_range != '-1':
            min_price, max_price = price_range.split('-')
            query = query.filter(price__gte=int(min_price), price__lte=int(max_price))
            
        if status != 'all':
            query = query.filter(status=status)
            
        # Lấy dữ liệu
        products = query.order_by('id')
        
        # Tạo DataFrame
        data = []
        for product in products:
            data.append({
                'ID': product.id,
                'Tên sản phẩm': product.name,
                'Danh mục': product.category.name if product.category else 'Không có danh mục',
                'Giá': f"{product.price:,} VND",
                'Mô tả': product.description,
                'Trạng thái': 'Đang bán' if product.status == 'active' else 'Ngừng bán',
                'Ngày tạo': product.created_at.strftime('%d/%m/%Y %H:%M')
            })
            
        df = pd.DataFrame(data)
        
        # Tạo Excel file
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Danh sách sản phẩm', index=False)
        
        # Định dạng Excel
        workbook = writer.book
        worksheet = writer.sheets['Danh sách sản phẩm']
        
        # Định dạng header
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # Áp dụng định dạng cho header
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        # Điều chỉnh độ rộng cột
        for i, col in enumerate(df.columns):
            column_width = max(df[col].astype(str).map(len).max(), len(col) + 2)
            worksheet.set_column(i, i, column_width)
            
        writer.close()
        
        # Trả về file Excel
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=danh_sach_san_pham.xlsx'
        
        return response
    
    
class IngredientProductForm(forms.ModelForm):
    class Meta:
        model = IngredientProduct
        fields = ['ingredient', 'quantity_required']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'quantity_required': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '1'}),
        }


IngredientProductFormSet = inlineformset_factory(
    Product, IngredientProduct,
    form=IngredientProductForm,
    extra=1,  # Số lượng nguyên liệu mặc định hiển thị
    can_delete=True  # Cho phép xóa nguyên liệu khỏi sản phẩm
)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'description', 'image']
        labels = {
            'name': 'Tên sản phẩm',
            'category': 'Loại sản phẩm',
            'price': 'Giá',
            'description': 'Mô tả',
            'image': 'Hình ảnh',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'category': forms.Select(attrs={'id': 'category-select', 'class': 'form-control form-control-sm-'}),
            'price': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2}),
            'image': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'accept': 'image/jpeg,image/png'}),
        }


@login_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        print('form', form)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True, "message": "Thêm sản phẩm thành công!"}, status=200)
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = ProductForm()

    return render(request, 'apps/web_01/modal/content/content_add_product.html', {'form': form})


@login_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        # Lấy danh sách nguyên liệu + số lượng từ request
        ingredient_data = json.loads(request.POST.get('ingredients', '[]'))  # [{id: 1, quantity: 2}, ...]

        if form.is_valid():
            product = form.save()

            # Xóa nguyên liệu cũ (nếu có)
            IngredientProduct.objects.filter(product=product).delete()

            # Lưu mới nguyên liệu kèm số lượng
            for item in ingredient_data:
                ingredient_id = item.get('id')
                quantity = item.get('quantity', 1)

                if ingredient_id:
                    ingredient = Ingredient.objects.get(id=ingredient_id)
                    IngredientProduct.objects.create(
                        product=product,
                        ingredient=ingredient,
                        quantity_required=quantity
                    )

            return JsonResponse({"success": True, "message": "Thêm sản phẩm thành công!"}, status=200)

        return JsonResponse({"success": False, "errors": form.errors}, status=400)

    else:
        form = ProductForm()
        ingredients = Ingredient.objects.all()  # Lấy danh sách nguyên liệu

    return render(request, 'apps/web_01/modal/content/content_add_product.html', {
        'form': form,
        'ingredients': ingredients
    })


@login_required
def import_product(request):
    if request.method == "POST" and request.FILES.get("excelFile"):
        file = request.FILES["excelFile"]
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)

        # Lưu file Excel vào thư mục media
        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Đọc file Excel
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Lỗi khi đọc file Excel: {e}"})

        # Lặp qua từng dòng trong file Excel
        for index, row in df.iterrows():
            try:
                product_name = row["Tên sản phẩm"]
                description = row.get("Mô tả", "")
                price = row.get("Giá", 0)
                image_url = row.get("Ảnh", "").strip()
                category_name = row.get("Danh mục", "").strip()
                ingredients_data = row.get("Nguyên liệu", "")

                # Xử lý danh mục
                category = None
                if category_name:
                    category, _ = Category.objects.get_or_create(name=category_name)

                # Tải ảnh lên Cloudinary
                image_cloud_url = None
                if image_url:
                    try:
                        uploaded_image = cloudinary.uploader.upload(image_url)
                        image_cloud_url = uploaded_image.get("secure_url")
                    except Exception as e:
                        print(f"❌ Lỗi khi tải ảnh từ {image_url}: {e}")

                # Tạo hoặc cập nhật sản phẩm
                product, created = Product.objects.update_or_create(
                    name=product_name,
                    defaults={
                        "description": description,
                        "price": price,
                        "image": image_cloud_url,
                        "category": category,
                    },
                )

                # Xóa nguyên liệu cũ
                IngredientProduct.objects.filter(product=product).delete()

                # Thêm nguyên liệu mới
                if ingredients_data and isinstance(ingredients_data, str):
                    for item in ingredients_data.split(","):
                        try:
                            ingredient_id, quantity = map(str.strip, item.split(":"))
                            ingredient = Ingredient.objects.get(id=int(ingredient_id))
                            IngredientProduct.objects.create(
                                product=product, ingredient=ingredient, quantity_required=int(quantity)
                            )
                        except Exception as e:
                            print(f"❌ Lỗi thêm nguyên liệu cho {product_name}: {e}")

            except Exception as e:
                print(f"❌ Lỗi khi xử lý dòng {index + 1}: {e}")

        # Xóa file đã nhập
        if os.path.exists(file_path):
            os.remove(file_path)
        return JsonResponse({"success": True, "message": "Nhập sản phẩm thành công!"})

    return render(request, 'apps/web_01/modal/content/content_import_product.html', {})


@login_required
def detail_product(request, id):
    product = get_object_or_404(Product.objects.select_related("category"), id=id)
    ingredients = IngredientProduct.objects.filter(product=product).select_related("ingredient")

    context = {
        "product": product,
        "ingredients": ingredients
    }
    return render(request, "apps/web_01/modal/content/content_detail_product.html", context)


def best_seller(request):
    now = timezone.now()
    first_day_this_month = now.replace(day=1)
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)

    # Doanh số tháng hiện tại
    current_sales = (
        OrderDetail.objects
        .filter(created_at__gte=first_day_this_month)
        .values('product__id', 'product__name', 'product__price', 'product__image', 'product__category__name')
        .annotate(total_sales=Sum('quantity'))
    )

    # Doanh số tháng trước
    previous_sales = (
        OrderDetail.objects
        .filter(created_at__gte=first_day_last_month, created_at__lt=first_day_this_month)
        .values('product__id')
        .annotate(previous_sales=Sum('quantity'))
    )

    # Map previous_sales để dễ truy cập
    previous_map = {item['product__id']: item['previous_sales'] for item in previous_sales}

    # Tính growth %
    best_sellers = []
    for item in current_sales:
        product_id = item['product__id']
        current = item['total_sales']
        previous = previous_map.get(product_id, 0)

        if previous == 0:
            growth = 100 if current > 0 else 0
        else:
            growth = round(((current - previous) / previous) * 100)

        item['growth'] = growth
        best_sellers.append(item)

    # Sắp xếp theo current sales giảm dần và lấy top 10
    best_sellers = sorted(best_sellers, key=lambda x: x['total_sales'], reverse=True)[:10]

    return render(request, "apps/web_01/dashboard/best_seller.html", {"best_sellers": best_sellers})


class ProductEditView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        try:
            product_id = request.GET.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            
            # Lấy danh sách danh mục cho dropdown
            categories = Category.objects.filter(status='active')
            
            # Render template chỉnh sửa sản phẩm
           
            return render(request, 'apps/web_01/modal/content/content_edit_product.html',{
                'product': product,
                'categories': categories,
            }) 
           
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    def post(self, request, *args, **kwargs):
        try:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            
            # Cập nhật thông tin sản phẩm
            product.name = request.POST.get('name')
            product.category_id = request.POST.get('category')
            product.price = request.POST.get('price')
            product.description = request.POST.get('description')
            status = request.POST.get('status')
            product.status =  'active' if status == 'active' else 'inactive'
            product.is_featured = request.POST.get('is_featured') == 'on'
            
            # Xử lý hình ảnh nếu có
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            
            # Lưu thay đổi
            product.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Cập nhật sản phẩm thành công'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)