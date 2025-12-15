import re
from models import Project, Volume, Chapter, Worldview, RPGCharacter, Organization, SupernaturalPower, Weapon, Dungeon

def process_prompt_template(db, prompt_template, project_id, request_resources=None, selected_text=None):
    content = prompt_template.content

    if '{{' not in content:
        return content

    search_models = [
        RPGCharacter, Organization, SupernaturalPower, Weapon, Dungeon, Chapter, Volume, Project
    ]

    def replacer(match):
        keyword = match.group(1).strip()
        print(f"--- Searching for keyword: '{keyword}' ---")
        
        # 特殊处理：选择文字
        if keyword == "选择文字":
            if selected_text:
                print(f"[SUCCESS] Found selected text")
                return str(selected_text)
            else:
                print(f"--- No selected text provided ---")
                return match.group(0)
        
        # 特殊处理：世界观
        if keyword == "世界观" and project_id:
            worldview = db.query(Worldview).filter(Worldview.project_id == project_id).first()
            if worldview and worldview.content:
                print(f"[SUCCESS] Found worldview")
                return str(worldview.content)
        
        if not project_id:
            return match.group(0)

        for model in search_models:
            model_name = model.__name__
            query = db.query(model)
            query_attr = 'name' if hasattr(model, 'name') else 'title'

            if model == Chapter:
                query = query.filter(Chapter.project_id == project_id, Chapter.title.startswith(keyword))
            elif hasattr(model, 'project_id'):
                query = query.filter(model.project_id == project_id, getattr(model, query_attr) == keyword)
            else:
                # This case would be for models not tied to a project, like Project itself by title
                query = query.filter(getattr(model, query_attr) == keyword)

            result = query.first()
            
            if result:
                print(f"[SUCCESS] Found match in {model_name} for keyword '{keyword}'")
                found_content = None
                if hasattr(result, 'content') and result.content:
                    found_content = result.content
                elif hasattr(result, 'description') and result.description:
                    found_content = result.description
                else:
                    found_content = getattr(result, query_attr, '')
                
                # Return the found content for replacement
                return str(found_content)

        # If no match was found in any model, return the original placeholder
        print(f"--- Keyword '{{{{ {keyword} }}}}' was not found in any resource. ---")
        return match.group(0)

    # Use re.sub with the replacer function to perform all replacements
    final_content = re.sub(r'\{\{\s*(.*?)\s*\}\}', replacer, content)
    
    return final_content