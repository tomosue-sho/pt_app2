from django.shortcuts import render, get_object_or_404
from pt_kokushi.models.learning_models import LearningMaterial
from django.db.models import Count

def learning_material_list(request):
    # 分野ごとに資料をグループ化
    materials_by_field = LearningMaterial.objects.values('field').annotate(total=Count('id')).order_by('field')
    
    # 各分野に属する資料のリストを取得
    materials_dict = {}
    for item in materials_by_field:
        materials = LearningMaterial.objects.filter(field=item['field'])
        materials_dict[item['field']] = materials

    return render(request, 'learning_materials/learning_list.html', {'materials_dict': materials_dict})
