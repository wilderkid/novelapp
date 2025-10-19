import re
from models import Worldview, RPGCharacter, Organization, SupernaturalPower, Weapon, Dungeon

def process_prompt_template(db, prompt_template, request_resources=None):
    """
    处理提示词模板，替换其中的变量引用

    参数:
        db: 数据库会话
        prompt_template: 提示词模板对象
        request_resources: 请求中传递的资源字典

    返回:
        处理后的提示词字符串
    """
    # 获取提示词所属的项目ID（如果有的话）
    project_id = prompt_template.project_id

    # 初始化资源字典
    resources = {}

    # 如果提示词关联了项目，则从项目中获取资源
    if project_id:
        # 获取世界观资源
        worldviews = db.query(Worldview).filter(Worldview.project_id == project_id).all()
        for worldview in worldviews:
            resources[worldview.name] = worldview.content

        # 获取角色资源
        characters = db.query(RPGCharacter).filter(RPGCharacter.project_id == project_id).all()
        for character in characters:
            resources[character.name] = character.content

        # 获取组织资源
        organizations = db.query(Organization).filter(Organization.project_id == project_id).all()
        for organization in organizations:
            resources[organization.name] = organization.content

        # 获取超能力资源
        powers = db.query(SupernaturalPower).filter(SupernaturalPower.project_id == project_id).all()
        for power in powers:
            resources[power.name] = power.content

        # 获取武器资源
        weapons = db.query(Weapon).filter(Weapon.project_id == project_id).all()
        for weapon in weapons:
            resources[weapon.name] = weapon.content

        # 获取地下城资源
        dungeons = db.query(Dungeon).filter(Dungeon.project_id == project_id).all()
        for dungeon in dungeons:
            resources[dungeon.name] = dungeon.content

    # 如果请求中包含资源数据，则添加到资源字典
    if request_resources:
        for key, value in request_resources.items():
            resources[key] = value
            print(f"添加资源: {key} = {value}")

    # 从提示词中提取所有变量名
    import re
    variable_names = re.findall(r'\{\{([^}]+)\}\}', prompt_template.content)
    print(f"从提示词中提取的变量名: {variable_names}")

    # 尝试从数据库中获取每个角色的数据
    for var_name in variable_names:
        clean_name = var_name.strip()  # 去除变量名前后的空格
        if clean_name not in resources:
            # 尝试从RPGCharacter表中获取角色数据
            character = db.query(RPGCharacter).filter(RPGCharacter.name == clean_name).first()
            if character:
                resources[clean_name] = character.content
                print(f"从数据库获取角色: {clean_name} = {character.content}")
            else:
                print(f"在数据库中未找到角色: {clean_name}")

    # 输出资源字典内容
    print("资源字典内容:", resources)
    print("原始提示词:", prompt_template.content)

    # 使用正则表达式查找并替换资源引用
    def replace_resource_reference(match):
        resource_name = match.group(1).strip()  # 去除变量名前后的空格
        print(f"尝试替换变量: '{resource_name}'")
        replacement = resources.get(resource_name, match.group(0))  # 如果找不到资源，保留原始引用
        print(f"替换结果: {replacement}")
        return replacement

    # 替换提示词中的资源引用
    system_prompt = re.sub(r'\{\{([^}]+)\}\}', replace_resource_reference, prompt_template.content)
    print("处理后提示词:", system_prompt)

    # 返回处理后的提示词
    return system_prompt
