def is_valid_description(description):
    return (
        description and
        isinstance(description, str)
    )


def is_valid_title(title):
    return (
        title and
        isinstance(title, str)
    )


def is_valid_company(company):
    return (
        company and
        isinstance(company, str)
    )


def filter_job_by_description(job, config):
    valid_description = is_valid_description(job['job_description'])
    desc_check = any(word.lower() in job['job_description'].lower() for word in config['desc_words'])

    if not valid_description:
        print(f"Invalid description for job: {job}")
    elif not desc_check:
        print(f"Description filter failed for job: {job}")

    return valid_description and desc_check


def filter_job_by_title(job, config):
    is_valid = is_valid_title(job['title'])

    title_words = config.get('title_include', [])  # Replace with your actual configuration key

    if not is_valid:
        print(f"Invalid title for job: {job}")
        return False

    if title_words is None:
        print(f"Title words is None for job: {job}")
        return job

    title_include_check = any(word.lower() in job['title'].lower() for word in title_words)
    title_exclude_check = any(word.lower() not in job['title'].lower() for word in config.get('title_exclude', []))

    if not title_include_check or not title_exclude_check:
        print(f"Title filter failed for job: {job}")

    return job if title_include_check and title_exclude_check else None



def filter_job_by_company(job, config):
    return (
        is_valid_company(job['company']) and
        all(word.lower() not in job['company'].lower() for word in config['company_exclude'])
    )
