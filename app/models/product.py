"""Defines data models used by /api/product endpoints."""
import os
from datetime import datetime, timezone

from sqlalchemy.ext.hybrid import hybrid_property

from app import db
from app.util.dt_format_strings import DT_FORMAT_ISO


class Product(db.Model):
    __tablename__ = 'release_info'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(), unique=True)
    release_info_url = db.Column(db.String(), unique=False)
    xpath_version_number = db.Column(db.String(), unique=False)
    xpath_download_url = db.Column(db.String(), unique=False)
    newest_version_number = db.Column(db.String(), unique=False)
    download_url = db.Column(db.String(), unique=False)
    last_update = db.Column(db.DateTime, nullable=True, default=datetime.min)
    last_checked = db.Column(db.DateTime, nullable=True, default=datetime.min)

    @hybrid_property
    def last_update_utc_iso(self):
        return self.last_update.replace(tzinfo=timezone.utc)\
            .strftime(DT_FORMAT_ISO) if self.last_update else None

    @hybrid_property
    def last_checked_utc_iso(self):
        return self.last_checked.replace(tzinfo=timezone.utc)\
            .strftime(DT_FORMAT_ISO) if self.last_checked else None

    def __init__(
        self,
        product_name,
        release_info_url=None,
        xpath_version_number=None,
        xpath_download_url=None,
        newest_version_number=None,
        download_url=None,
        last_update=None,
        last_checked=None
    ):
        if xpath_version_number is None:
            xpath_version_number = ""
        if xpath_download_url is None:
            xpath_download_url = ""
        if newest_version_number is None:
            newest_version_number = ""
        if download_url is None:
            download_url = ""
        if last_update is None:
            last_update = datetime.min
        if last_checked is None:
            last_checked = datetime.min

        self.product_name = product_name
        self.release_info_url = release_info_url
        self.xpath_version_number = xpath_version_number
        self.xpath_download_url = xpath_download_url
        self.newest_version_number = newest_version_number
        self.download_url = download_url
        self.last_update = last_update
        self.last_checked = last_checked

    def __repr__(self):
        return (
            '<Product('
                'id={id},'
                'product_name={name},'
                'newest_version_number={version})>'
        ).format(
            id=self.id,
            name=self.product_name,
            version=self.newest_version_number
        )

    @classmethod
    def find_by_name(cls, product_name):
        return cls.query.filter_by(product_name=product_name).first()