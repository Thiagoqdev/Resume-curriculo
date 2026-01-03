from uuid import uuid4
from datetime import datetime
from models.domain import Resume, ResumeStatus


def create_new_resume(self, user_id: uuid4, dto: ResumeCreateRequest) -> Resume:
    resume_group_id = uuid4()

    resume = Resume(
        resume_id=uuid4(),
        resume_group_id=resume_group_id,
        user_id=user_id,
        title=dto.title,
        version_number=1,
        version="v1.0",
        is_current=True,
        status=ResumeStatus.DRAFT,
        original_filename=dto.original_filename,
        file_size=dto.file_size,
        file_type=dto.file_type,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    return self.resume_repository.add(resume)

def search_resume(self, user_id: UIDD, resume_id: UUID) -> Resume:
   resume =  self.resume_repository.get_by__id(resume_id)

   if not resume:
       raise ValueError("Resume not found")
   
   if resume.user_id != user_id:
       raise PermissionError("Access denied to this resume")
   
   return resume



