# Generated for Task T-047

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contact", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="contactmessage",
            old_name="name",
            new_name="sender_name",
        ),
        migrations.AlterField(
            model_name="contactmessage",
            name="sender_name",
            field=models.CharField(max_length=120, verbose_name="Sender Name"),
        ),
        migrations.AlterField(
            model_name="contactmessage",
            name="email",
            field=models.EmailField(max_length=254, verbose_name="Email"),
        ),
        migrations.AlterField(
            model_name="contactmessage",
            name="subject",
            field=models.CharField(blank=True, default="", max_length=200, verbose_name="Subject"),
        ),
        migrations.AlterField(
            model_name="contactmessage",
            name="message",
            field=models.TextField(max_length=3000, verbose_name="Message"),
        ),
        migrations.AlterField(
            model_name="contactmessage",
            name="ip_address",
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name="IP Address"),
        ),
        migrations.AlterField(
            model_name="contactmessage",
            name="is_read",
            field=models.BooleanField(default=False, verbose_name="Is Read"),
        ),
        migrations.AlterField(
            model_name="contactmessage",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
        ),
        migrations.AddField(
            model_name="contactmessage",
            name="is_notified",
            field=models.BooleanField(default=False, verbose_name="Is Notification Sent"),
        ),
    ]
